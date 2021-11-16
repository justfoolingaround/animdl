<h1><center>Bypassing Cloudflare</center></h1>

<h2>When using the client</h2>

This project comes with an internal mechanisms to remove any problems in scraping. However, this will require **you**, as an user to cooperate with the instructions provided from within the project.

The prompt for a cloudflare bypass will look like:

<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910035620246741012/unknown.png">
</center>

<br>

What you will need to do, is, go to the url that the project says you'll need to go to, in this case, it is (Highlighted in **yellow** or `https://animeout.xyz/?s=kaguya`):


<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910037851079602276/unknown.png">
</center>
<br>

You need to now go to that site and wait for it to fully load, just how you'd expect the site to see.

The value you need is a cookie. You can get the cookies of a site by clicking on the padlock icon. Then you can click on the cookies.

> Note: This project will never **save** your valuable `cf_clearance`. To top it off, it would be meaningless to anyone but you.

<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910038898430857266/unknown.png">
</center>

Now, you can just simply use your intuition to navigate to the `cf_clearance` and copy it.

<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910039353143722074/unknown.png">
</center>

All that remains is to paste the value to the project's prompt.

<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910040133418491984/unknown.png">
</center>

And now, what you'll need to do, is to find your browser's `User-Agent`. This is due to the fact that, `cf_clearance` is based off some factors. `User-Agent` is one of it. Since the project can perfectly handle other factors, all you need to do is, supply it with the `User-Agent` of your browser. 

**Keep in mind that this needs to be browser where you fetched the `cf_clearance` from.**

Incognito mode will not make a difference.

This can be found in your browser's about page.

`about:about` is a general page that redirects to the browser's about page, however, since it failed in Vivaldi (A Chromium browser), it is suggested to use `chrome://version` for Chromium browsers as it will redirect to the about page. 

<center>
<img src="https://media.discordapp.net/attachments/854704235139301386/910041897039433728/unknown.png">
</center>

All you need to do now, is to copy that value and paste it.

Don't worry, you'll only be prompted about this once-per-session.

<h2>When streaming content</h2>

Your player may not be able to stream the content since it lacks `cf_clearance` and the mentioned `User-Agent`.

What you will need to do now will be to provide necessary `player-opts` to the project when using `stream`.

Since this is a difficult procedure as it will vary over your player used, it is not recommended to stream the content that is cloudflare protected.

As of right now, the following providers may not be able to stream content without the `player-opts`.

- AnimeOut

> Note: `player-opts` set to
`--http-header-fields=cookie=cf_clearance={cf_clearance} user-agent={user-agent}` will work for `mpv` / `iina` in case of AnimeOut.
