# trifold

A quick way to deploy static projects to a fast, cheap, and reliable CDN.

`trifold` deploys a directory of HTML/CSS/JS to a CDN.

## create a bunny.net account

bunny.net is a CDN with great prices and an easy-to-use API. (The authors have no affiliation with the service.)
For a few cents per GB you can host a static site using their storage & pull zones.

If you'd like to [sign up with our affiliate link](https://bunny.net?ref=h2lzic0ige), when you pay to h;ost your site, we'll earn a commission at no extra cost to you!

If you'd prefer not to, you can sign up by visiting bunny.net.

Once you have an account, visit <https://dash.bunny.net/account/api-key> to obtain your API key.

To use the commands below you'll need to set the `BUNNY_API_KEY` environment variable:

```sh
$ export BUNNY_API_KEY=1234...         # replace with your key
```

## usage

To get started, your project needs a `trifold.toml`.

Generate one with:

```sh
$ uvx trifold init
```

This will ask you a few questions, create the necessary remote resources, and write a `trifold.toml` file locally.

TODO: document questions

Note: The default behavior is to only serve data from North America, which costs $0.01/GB in bandwidth. Other regions are available at an additional cost, and can be configured via the web interface (CDN->General->Pricing & routing).

With a zone created, we're ready to publish, but it's always a good idea to look before you leap-- let's check the status:

```sh
$ uvx trifold status -v
```

This shows us the files that will be uploaded or deleted.

Run:

```sh
$ uvx trifold publish
```

After a few seconds, your files are uploaded to the CDN.

By default, for safety, this will only create or update files.
If you'd like it to delete remote files that are no longer in your local directory add `--delete`.

*This command will never modify your local files!*

Now your site is hosted at `your-zone-name.b-cdn.net`!

If you'd like to add a custom domain, there's one more command to run.

Before you run this command, create a DNS CNAME or ALIAS record pointing your domain at `your-zone-name.b-cdn.net`.

Once that's done, wait 5-10 minutes for propagation, then:

```sh
$ uvx trifold domain-add example.com
```

This will configure an SSL certificate and force SSL.

## why?

This project grew out of my frustration with services making their free tier less friendly to indie devs & students that just need a cheap & reliable place they can host things.

Instead of relying on a free service it is hopefully going to be more stable to rely on a paid service with a reasonable price point (and the ability to set billing limits).
