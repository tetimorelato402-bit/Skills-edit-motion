//  AnvilSplash.swift
//
//  The launch animation, as the app should run it. This is a line-for-line port
//  of splash.html — same traced profile, same constants, same curves — so the
//  reference render (anvil-splash.mp4) is what this draws, not an impression
//  of it. Numbers are in POINTS on a 393 x 852 artboard, matching
//  005-anvil/source/screens.html.
//
//  WHY IT IS A Canvas AND NOT rotation3DEffect
//  -------------------------------------------
//  rotation3DEffect takes a flat view and skews it in perspective. That is a
//  sticker turning, and it is precisely what made the old animation read badly:
//  the mark has no thickness, so the only thing a 3D rotation can do to it is
//  distort its silhouette. This draws an actual extruded solid — front cap, back
//  cap, and a wall quad per edge — then culls, depth-sorts and lights it. At
//  rest the solid is face-on, so what is on screen is the front cap, which is
//  the logo exactly. There is nothing to cross-fade to.
//
//  USAGE
//  -----
//      AnvilSplash { showMainApp = true }
//
//  It calls back at T_OUT. Nothing else is on screen: no wordmark, no tagline.

import SwiftUI
import simd

// MARK: - Palette

private enum Anvil {
    /// Measured off the build — 005-anvil/BRIEF.md.
    static let bone = Color(red: 0xE3/255, green: 0xDA/255, blue: 0xCD/255)
    static let ink  = Color(red: 0x23/255, green: 0x1C/255, blue: 0x15/255)
    /// The walls run ink -> gold. The range is wide on purpose: a first pass ran
    /// them within a few values of the ink face and the solid read as a flat
    /// shape being skewed, which is the whole failure the extrusion exists to
    /// avoid. An extrusion you cannot tell from its own front cap is not one.
    static let wallDark = SIMD3<Double>(0x2A, 0x20, 0x15)
    static let wallLit  = SIMD3<Double>(0x9E, 0x7C, 0x52)
}

// MARK: - The mark

/// The logo's geometry, traced off the artwork by scanline at 1% of its height.
/// `halfWidth` is a fraction of the FULL width; `y` runs 0 at the top edge to 1
/// at the foot. Each entry is where the measured half-width steps or changes
/// slope, so this is the mark's geometry and not a drawing of it.
private let profile: [(halfWidth: Double, y: Double)] = [
    (0.4971, 0.000),   // top edge, full width
    (0.3480, 0.295),   // bottom of the plate's taper
    (0.1579, 0.295),   // the overhang: a horizontal step in
    (0.1579, 0.605),   // the waist, straight
    (0.2485, 0.940),   // the base, flared
    (0.0936, 0.940),   // the foot: a second step in
    (0.0906, 1.000),   // the foot's bottom
]

/// Measured off the artwork's bounding box, 343 x 184.
private let aspect = 343.0 / 184.0
private let footY = (1.0 - 0.5) / aspect

/// Closed outline: down the right side, back up the mirrored left.
private let outline: [SIMD2<Double>] = {
    var pts = profile.map { SIMD2($0.halfWidth, ($0.y - 0.5) / aspect) }
    pts += profile.reversed().map { SIMD2(-$0.halfWidth, ($0.y - 0.5) / aspect) }
    return pts
}()

// MARK: - Layout and clock

private enum Spec {
    static let logoWidth = 176.0        // pt, measured off the TestFlight recording
    static let centreY   = 0.455        // of the screen height. Losing the wordmark
                                        // removes what was UNDER the mark; it does
                                        // not move the mark.
    static let depth     = 0.260        // extrusion, as a fraction of the width
    static let camera    = 3.4          // camera distance, in width units

    static let land  = 0.44             // ONE landing frame: everything resolves here
    static let settle = 0.60            // the compression is finished
    static let hold  = 1.05             // dead still until here
    static let out   = 1.35             // handed over to the app
    static let total = 1.45
}

// MARK: - Curves

/// The fall ACCELERATES. An out-curve decelerates into the landing, so the mark
/// is already standing still before it arrives and the impact has nothing to
/// absorb — which is what made the original feel soft. Gravity is u squared: it
/// is moving fastest on the frame it lands, and the compression takes that out.
private func gravity(_ u: Double) -> Double { u * u }

/// The turn is LINEAR and the floor is what stops it. Nothing slows a spin in
/// mid-air, so an eased rotation leaves the mark square and motionless a tenth
/// of a second before touchdown — two events, a turn and then a drop, when the
/// whole point is that it is one.
private func turn(_ u: Double) -> Double { u }

private func outCubic(_ u: Double) -> Double { 1 - pow(1 - u, 3) }
private func clamp01(_ v: Double) -> Double { min(1, max(0, v)) }
private func lerp(_ a: Double, _ b: Double, _ u: Double) -> Double { a + (b - a) * u }

// MARK: - 3D

private struct Face {
    var points: [CGPoint]
    var depth: Double
    var normal: SIMD3<Double>
    var isFront: Bool
}

private func rotation(yaw: Double, pitch: Double, roll: Double) -> (SIMD3<Double>, SIMD3<Double>, SIMD3<Double>) {
    let cy = cos(yaw),   sy = sin(yaw)
    let cx = cos(pitch), sx = sin(pitch)
    let cz = cos(roll),  sz = sin(roll)
    return (SIMD3(cz*cy + sz*sx*sy, -sz*cx,  -cz*sy + sz*sx*cy),
            SIMD3(sz*cy - cz*sx*sy,  cz*cx,  -sz*sy - cz*sx*cy),
            SIMD3(cx*sy,             sx,      cx*cy))
}

/// One key light, upper-left and in front. The top plate's upper face is what
/// catches it, and that single plane is what stops the turn reading as a flat
/// shape being skewed.
private let key = simd_normalize(SIMD3<Double>(-0.40, -0.74, 0.54))

private func wallColour(_ n: SIMD3<Double>) -> Color {
    let u = pow(max(0, simd_dot(n, key)), 0.85)
    let c = Anvil.wallDark + (Anvil.wallLit - Anvil.wallDark) * u
    return Color(red: c.x/255, green: c.y/255, blue: c.z/255)
}

// MARK: - Drawing

private func drawSolid(_ ctx: inout GraphicsContext,
                       centre: CGPoint, scale S: Double,
                       yaw: Double, pitch: Double, roll: Double,
                       squashX: Double, squashY: Double) {
    let (r0, r1, r2) = rotation(yaw: yaw, pitch: pitch, roll: roll)
    func apply(_ v: SIMD3<Double>) -> SIMD3<Double> {
        SIMD3(simd_dot(r0, v), simd_dot(r1, v), simd_dot(r2, v))
    }
    let d = Spec.depth / 2
    let front = outline.map { apply(SIMD3($0.x, $0.y,  d)) }
    let back  = outline.map { apply(SIMD3($0.x, $0.y, -d)) }

    /// The squash is applied in SCREEN space about the FOOT, because the anvil
    /// is sitting on something. Compressing about its centre would be a jelly.
    func project(_ v: SIMD3<Double>) -> CGPoint {
        let f = Spec.camera / (Spec.camera - v.z)
        let x = v.x * f * S, y = v.y * f * S
        let base = footY * S
        return CGPoint(x: centre.x + x * squashX,
                       y: centre.y + base + (y - base) * squashY)
    }

    var faces: [Face] = []
    func add(_ vs: [SIMD3<Double>], isFront: Bool = false) {
        let n = simd_normalize(simd_cross(vs[1] - vs[0], vs[2] - vs[0]))
        guard n.z > 0.001 else { return }                 // facing away
        faces.append(Face(points: vs.map(project),
                          depth: vs.reduce(0) { $0 + $1.z } / Double(vs.count),
                          normal: n, isFront: isFront))
    }

    // WINDING: `outline` runs down the right side and back up the left, and
    // model y increases downward, so the front cap as written has a +z normal.
    // The walls therefore have to be F,B,B,F and NOT F,F,B,B — the obvious order
    // gives every side an INWARD normal, which culls exactly the wrong half of
    // the solid and shades whatever survives from the wrong side. It does not
    // error. It just comes back as a mangled silhouette.
    for i in outline.indices {
        let j = (i + 1) % outline.count
        add([front[i], back[i], back[j], front[j]])
    }
    add(front, isFront: true)                             // the front cap: the logo
    add(back.reversed())                                  // the back cap

    // Painter's algorithm, because this profile is CONCAVE at the overhang and
    // at the foot — culling alone would let the plate's underside paint over
    // the waist.
    for face in faces.sorted(by: { $0.depth < $1.depth }) {
        var path = Path()
        path.addLines(face.points)
        path.closeSubpath()
        // The front cap is the logo and is never shaded. Everything else is the
        // solid the logo is cut out of.
        ctx.fill(path, with: .color(face.isFront ? Anvil.ink : wallColour(face.normal)))
    }
}

// MARK: - The view

struct AnvilSplash: View {
    /// Called once, at T_OUT, when the app should be on screen underneath.
    var onFinished: () -> Void = {}

    @State private var start = Date.now
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        TimelineView(.animation) { timeline in
            let t = min(Spec.total, timeline.date.timeIntervalSince(start))
            Canvas { ctx, size in render(&ctx, size: size, t: t) }
        }
        .background(Anvil.bone)
        .ignoresSafeArea()
        // The whole piece is one object arriving. There is nothing to read, so
        // there is nothing to describe beyond what it is.
        .accessibilityElement()
        .accessibilityLabel("Anvil")
        .onAppear { start = .now }
        // Not driven off the render closure: mutating state from inside a
        // TimelineView update is a good way to get a runtime warning and a
        // dropped frame on the one frame that matters.
        .task {
            try? await Task.sleep(for: .seconds(Spec.out))
            onFinished()
        }
    }

    private func render(_ ctx: inout GraphicsContext, size: CGSize, t: Double) {
        // Reduce Motion gets the mark, held, and the same handover. A splash is
        // not worth a vestibular problem, and a logo that simply IS there is a
        // perfectly good splash.
        guard !reduceMotion else {
            var alpha = 1.0
            if t >= Spec.hold { alpha = 1 - outCubic(clamp01((t - Spec.hold) / (Spec.out - Spec.hold))) }
            ctx.opacity = alpha
            drawSolid(&ctx,
                      centre: CGPoint(x: size.width / 2, y: size.height * Spec.centreY),
                      scale: Spec.logoWidth, yaw: 0, pitch: 0, roll: 0,
                      squashX: 1, squashY: 1)
            return
        }

        let raw = clamp01(t / Spec.land)
        let uf = gravity(raw), ut = turn(raw)
        let yaw   = lerp(-34, 0, ut) * .pi / 180
        // NEGATIVE pitch tips the top TOWARD the camera. Positive tips it away,
        // which puts the viewer under the anvil looking up at its base — the one
        // angle where the plate, the most recognisable thing about the mark, is
        // hidden.
        let pitch = lerp(-16, 0, ut) * .pi / 180
        let roll  = lerp(-4,  0, ut) * .pi / 180
        let drop  = lerp(-76, 0, uf)                 // pt above its resting place
        let scale = lerp(1.075, 1.0, uf)

        // The impact: one compression about the foot, and out. 0.955 is as far
        // as it goes and it is over in nine frames — a logo that visibly wobbles
        // is a toy.
        var squashX = 1.0, squashY = 1.0
        if t >= Spec.land && t < Spec.settle {
            let p = (t - Spec.land) / (Spec.settle - Spec.land)
            let k = sin(.pi * p) * pow(1 - p, 0.6)
            squashY = 1 - 0.045 * k
            squashX = 1 + 0.020 * k
        }

        // No fade in: iOS has already run its own app-open zoom to get here, and
        // a second transition on top of it is what makes a launch feel slow.
        var alpha = 1.0, exitScale = 1.0
        if t >= Spec.hold {
            let p = outCubic(clamp01((t - Spec.hold) / (Spec.out - Spec.hold)))
            alpha = 1 - p
            exitScale = lerp(1, 1.055, p)
        }
        guard alpha > 0.001 else { return }
        ctx.opacity = alpha

        let S = Spec.logoWidth * scale * exitScale
        let centre = CGPoint(x: size.width / 2, y: size.height * Spec.centreY + drop)

        // The ground it lands on. The shadow exists only around the impact: it
        // is what makes the mark an object that ARRIVED somewhere. Then it goes,
        // and what is left is the logo on a bone page with nothing under it.
        var shade = 0.0
        let lead = 2.0 / 60.0
        if t >= Spec.land - lead {
            shade = clamp01((t - (Spec.land - lead)) / (3.0 / 60.0))
                  * (1 - clamp01((t - Spec.settle) / 0.30))
        }
        if shade > 0.001 {
            let by = centre.y + footY * S + 3
            let rw = S * 0.46, rh = S * 0.058
            let rect = CGRect(x: centre.x - rw, y: by - rh, width: rw * 2, height: rh * 2)
            ctx.fill(Path(ellipseIn: rect),
                     with: .radialGradient(
                        Gradient(stops: [
                            .init(color: Anvil.ink.opacity(0.20 * shade), location: 0),
                            .init(color: Anvil.ink.opacity(0.09 * shade), location: 0.55),
                            .init(color: Anvil.ink.opacity(0),            location: 1),
                        ]),
                        center: CGPoint(x: centre.x, y: by),
                        startRadius: 0, endRadius: rw))
        }

        drawSolid(&ctx, centre: centre, scale: S,
                  yaw: yaw, pitch: pitch, roll: roll,
                  squashX: squashX, squashY: squashY)
    }
}

#Preview { AnvilSplash() }
