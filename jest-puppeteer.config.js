// These arguments are what jest-puppeteer specifies when running in CI
// (see https://github.com/argos-ci/jest-puppeteer/blob/main/packages/jest-environment-puppeteer/src/config.ts#L55-L63)
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

    // When running outside Docker, set `headless: false` to show the browser while tests run.
    devtools: false,
    headless: true,
  },
  browserContext: "incognito",
};
