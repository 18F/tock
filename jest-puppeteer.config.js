// These arguments are what jest-puppeteer specifies when running in CI
// (see https://github.com/smooth-code/jest-puppeteer/blob/master/packages/jest-environment-puppeteer/src/readConfig.js#L14-L24)
const DOCKER_LAUNCH_ARGS = [
  "--no-sandbox",
  "--disable-setuid-sandbox",
  "--disable-background-timer-throttling",
  "--disable-backgrounding-occluded-windows",
  "--disable-renderer-backgrounding",
];

module.exports = {
  port: parseInt(process.env.JEST_PORT, 10),

  launch: {
    args: process.env.IS_DOCKER ? DOCKER_LAUNCH_ARGS : [],

    // When running outside Docker, set `headless: true` to show the browser while tests run.
    devtools: false,
    headless: false,
  },
  browserContext: "incognito",
};
