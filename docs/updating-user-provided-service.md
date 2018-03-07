# Updating User-Provided Service for Tock

Tock leverages [Cloud Foundry User-Provided Service][cf-ups] to store
environment variables used in the running application. These values need to be
provided to the [cf-cli][] as valid JSON.

**Warning** You're dealing with sensitive information! None of the output of
these commands should be committed into a repository or shared in Slack.

Steps:

- Downloading User-Provided Service credentials
- Uploading User-Provided Service credentials

## Downloading User-Provided Service credentials

Run the following command:

```sh
cf env tock | grep -A20 'user-provided": \[' | grep -A20 'credentials": {'
```
With the output of this command, you will be capturing the JSON found inside of
`"credentials": { ... }`.


```

```

