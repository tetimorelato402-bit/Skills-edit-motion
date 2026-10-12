/* Fill these in before going live. Anything left empty is handled gracefully:
   no broken links, no "draft" notes shown to visitors. */
window.ANVIL = {
  // App Store page for the iPhone app.
  appStore: '',
  // Stripe Payment Links, one per billing period. Set the trial length on each
  // link in Stripe (7 days monthly, 21 days yearly) so it matches the page.
  stripeMonthly: '',
  stripeYearly: '',
  // Stripe customer portal, used on the Pause or cancel page.
  stripePortal: '',
  // Where people can reach a human. Shown in the footer and the FAQ.
  supportEmail: '',
  // Optional: an endpoint that accepts a JSON POST (Formspree, Basin, your own).
  // Creator submissions go here. Empty = the form opens an email instead.
  formEndpoint: ''
};
