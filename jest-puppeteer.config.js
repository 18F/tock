module.exports = {
  port: parseInt(process.env.JEST_PORT, 10),
  // the launch options are helpful for debugging purposes

  // launch: {
  //   headless: false,
  //   devtools: true,
  // },
  browserContext: "incognito"
};
