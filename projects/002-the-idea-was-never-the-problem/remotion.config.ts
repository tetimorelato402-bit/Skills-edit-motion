import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
Config.setChromiumDisableWebSecurity(false);
Config.setConcurrency(4);
// CRF 17 matches the house setting from study 001. A film about motion quality
// must not ship with compression artefacts on a flat BONE field.
Config.setCrf(17);
