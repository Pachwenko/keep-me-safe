# keep-me-safe
![Python Lint, MyPy, and Test](https://github.com/Pachwenko/keep-me-safe/workflows/Python%20Lint,%20MyPy,%20and%20Test/badge.svg)

Scrapes Iowa DOT 511 traffic pages for recent pictures and emails a list to myself.

## Usage

Can be run locally, but it is perferrable to run in [AWS Lambda](https://aws.amazon.com/lambda/) using [AWS SES](https://aws.amazon.com/ses/) to send emails.

Will always require 2 environment variables:

`KEEP_ME_SAFE_SENDER_EMAIL` - This will need to be [verified with AWS SES.](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses.html)

`KEEP_ME_SAFE_RECIPIENT_EMAIL`

Can alternatively use SendGrid, but I found this unreliable.

## Running manually
```
pip install -r requirements/base.txt
python keep_me_safe.py
```

## Generating Docs

```
pip install -r requirements/base.txt
pip install pdoc3
pdoc --html --output-dir documentation keep_me_safe --force
```

## Future plans

- Integrate with weather APIs and only send email if suspected rain/snow/etc.
- Include weather alert/forecasts if conditions are met for the email
- Integrate with waze/google maps/etc. to get commute time (the longer the commute, the more dangerous it is)
