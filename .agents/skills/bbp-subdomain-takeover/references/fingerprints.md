# Subdomain Takeover Fingerprints

Canonical response signatures for unclaimed third-party services.
Cross-reference with can-i-take-over-xyz for current exploitability ratings
(FINGERPRINTED / VULNERABLE / NOT-VULNERABLE).

Legend:
- Claimable = resource name is free; registering it yields control
- Verify    = fingerprint matches but ownership state needs manual check
- Skip      = signature alone does not prove takeover

## AWS

| Service | CNAME pattern | Fingerprint | State |
|---|---|---|---|
| S3 bucket | `*.s3.amazonaws.com`, `*.s3-website-<region>.amazonaws.com` | `NoSuchBucket` in body | Claimable if bucket name free |
| CloudFront | `*.cloudfront.net` | `Bad request. We can't connect to the server` / `ERROR: The request could not be satisfied` with missing dist | Verify distribution ownership |
| Elastic Beanstalk | `*.<region>.elasticbeanstalk.com` | `NXDOMAIN` root + no app | Claimable via new env same region |
| S3 static (ap-southeast) | `*.s3-website-ap-southeast-2.amazonaws.com` | `The specified bucket does not exist` | Claimable |
| AWS EB (legacy) | `*.elasticbeanstalk.com` | 404 from nginx | Verify |

## Azure

| Service | CNAME pattern | Fingerprint | State |
|---|---|---|---|
| App Services | `*.azurewebsites.net` | `404 Web Site not found.` | Claimable if name free |
| Cloud Services | `*.cloudapp.azure.com`, `*.cloudapp.net` | NXDOMAIN | Claimable |
| CDN | `*.azureedge.net`, `*.microsoftcdn.com` | `{ "statusCode": 400 }` w/ no endpoint | Claimable via new CDN profile |
| Front Door | `*.azurefd.net` | `The requested content does not exist.` | Verify |

## Google Cloud

| Service | CNAME pattern | Fingerprint | State |
|---|---|---|---|
| App Engine (custom) | `*.appspot.com` | `There is no app configured at that hostname` / dead app notice | Claimable if project free |
| Firebase Hosting | `*.web.app`, `*.firebaseapp.com` | `Site Not Found` | Claimable |

## PaaS / Static hosts

| Service | CNAME pattern | Fingerprint | State |
|---|---|---|---|
| GitHub Pages | `*.github.io` | `There isn't a GitHub Pages site here.` | Claimable if repo/org free |
| Heroku | `*.herokuapp.com`, `*.herokudns.com` | `No such app` | Claimable if name free |
| Fastly | `*.fastly.net`, `f*.cdn.ampproject.org` | `Fastly error: unknown domain:` | Claimable by adding domain to service |
| Surge.sh | `*.surge.sh` | `project not found` | Claimable |
| Render | `*.onrender.com` | `The application could not be found` | Claimable |
| Vercel | `*.vercel.app` | `DEPLOYMENT_NOT_FOUND` | Claimable if name free |
| Netlify | `*.netlify.app`, `*.netlify.com` | `Not Found - Request ID: ...` | Claimable |
| Pantheon | `*.pantheonsite.io` | `The gods are wise, but do not know of the site which you seek.` | Claimable |
| Readme.io | `*.readme.io` | `Project doesnt exist... yet!` | Claimable |
| Tilda | `*.tilda.ws` | `Please renew your subscription` / domain page | Verify |
| Webflow | `*.proxy-ssl.webflow.com`, `*.webflow.io` | `The page you are looking for doesn't exist or has been moved` | Verify |
| Wordpress.com | `*.wordpress.com` | `Do you want to register *.wordpress.com?` | Claimable |
| Tumblr | custom domains | `There's nothing here.` | Verify |
| Squarespace | `*.squarespace.com` | `Website Expired` | Verify |
| Cargo | `*.cargo.site` | `404 Not Found` + Cargo branding | Verify |
| Unbounce | `*.unbouncepages.com` | `The requested URL was not found on this server.` | Claimable |
| Instapage | `*.instapage.com` | 404 | Verify |

## SaaS / Helpdesk / Commerce

| Service | CNAME pattern | Fingerprint | State |
|---|---|---|---|
| Zendesk | `*.zendesk.com` | `Help Center Closed` | Claimable if subdomain free |
| Freshdesk | `*.freshdesk.com` | `We couldn't find this help center` / `Sorry, we couldn't find that page` | Claimable |
| Helpjuice | `*.helpjuice.com` | `We could not find what you're looking for` | Claimable |
| Helpscout | `*.helpscoutdocs.com` | `No settings were found for this company` | Claimable |
| Intercom | `custom.intercom.help` | `This page is reserved for artistic dogs.` | Claimable |
| Desk.com | `*.desk.com` | `Sorry, We Could Not Find That Page` | Verify |
| Shopify | `*.myshopify.com` | `Sorry, this shop is currently unavailable.` | Verify (strict name match) |
| BigCartel | `*.bigcartel.com` | `Page Not Found` | Verify |
| Tictail | `*.tictail.com` | `Building a brand of your own?` | Claimable |
| Ghost | `*.ghost.io` | `The thing you were looking for is no longer here...` | Claimable |
| Feedpress | `redirect.feedpress.me` | `The feed has not been found.` | Claimable |
| Pingdom | `stats.pingdom.com` | `Public Report Not Found` | Verify |
| Teamwork | `*.teamwork.com` | `Oops - We couldn't find that page` | Claimable |
| SurveyMonkey | custom | `There was a problem with your survey` | Verify |
| Bitbucket Cloud Pages | `*.bitbucket.io` | `Repository not found` | Claimable |
| GitLab Pages | `*.gitlab.io` | `404` w/ GitLab branding + empty project note | Verify |
| Short.io | custom | `Link does not exist` | Verify |
| Jetbrains Space | `*.jetbrains.space` | 404 | Verify |
| Aha! | `*.aha.io` | `There is no portal here ...` | Claimable |
| Brightcove | `*.bcvp0rtal.com`, players.brightcove.net | `<h1 class="bcplayer-error">` / video error | Verify |
| Campaign Monitor | `*.createsend.com` | `Trying to access your account page?` | Claimable |
| Acquia | `*.acquia-sites.com` | `The site you are looking for could not be found.` | Verify |
| Uptimerobot | no CNAME pattern | `page not found` | Skip |
| Mashery | `*.mashery.com` | `Unrecognized domain` | Claimable |
| Weatherstack | custom | service-specific error | Skip |

## NS delegation takeovers (highest impact)

Check NS records pointing to:

| Provider | Pattern | Check |
|---|---|---|
| AWS Route53 | `awsdns-*` | Delegated zone account deleted -> claim hosted zone with same 4 nameservers |
| Azure DNS | `*.azure.com` ns set | Zone removed from subscription |
| GCP Cloud DNS | `ns-cloud-*.googledomains.com` | Zone deleted; nameserver set reusable after grace period |
| Expired registrar NS | various | Domain lapsed; re-register |

Impact of NS takeover: full DNS control of subdomain including MX/SPF/DKIM
(email interception) — always report as critical.

## TXT / MX based verification

Some services verify domain ownership via TXT records before serving content
(e.g., Google Workspace, Atlassian). A stale TXT verification record can allow
claiming the SERVICE identity even without HTTP control:

```bash
dig +short TXT target.com | grep -Ei 'atlassian|google-site|ms=|facebook'
```

Report stale verification records separately: they enable email spoofing /
workspace hijack without any web takeover.
