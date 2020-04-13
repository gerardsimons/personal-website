---
title: "Moooooooo"
date: 2020-04-13T22:53:40+02:00
description: "The first post on my most modern website yet"
cover: "img/DSC1143.jpg" 
---

> "Hello, friend?" That's lame.
> Maybe I should give you a name...
> But that's a slippery slope.
> You're only in my head.
> We have to remember that...
> Shit.
> It's actually happened.
> I'm talking to an imaginary person.
>
> **— Mr. Robot S01E01**

# Hello ... ?
Ok that quote was actually the default first post of this website theme, but I liked it, so I kept it. [Big whoop, wanna fight about it](https://www.youtube.com/watch?v=30GD25un0XQ)? I can also recommend Mr. Robot as another good way to pass (corona) time fast and funnily. The cover photo is one I personally took last year on a trip to Scotland with my dear friend Georgios. The animal in the picture is not George. George is much hairier ~~LINK~~ *edit:I am not allowed by privacy laws to post a picture of his hairiness*. The cow doesn't really have so much to do with this post, but shaggy beasts are nice, are they not?

Anywho, hello, and welcome all, whoever you are. Though you are probably just me, constantly re-reading and     fretting over potential grammar mistakes. I am writing this during dire corona times and I thought it would **finally** be a good moment to make a website (again). 

# Old, in computer years
Just like you have dog years, similarly I think computer time is different, though I think 10x faster. So with 10+ years experience I feel old. Looking back, HTML4, CSS and - sorry for cursing - PHP really got me into web development and excited about the web as place where you marry technology and design in a very personal way. Back in the day I was just starting out at university. Then came all the gnarly JavaScript, the jQuery now there's a new framework every year, which was all very offputting to me. I think the last time I made a personal website, was for my small freelance business which was just a bare HTML. Before even that I am pretty sure I still used that whole LAMP stack with phpmyadmin and the likes, including paid hosting.

## Keeping Young with Hugo

![Image](https://d33wubrfki0l68.cloudfront.net/c38c7334cc3f23585738e40334284fddcaf03d5e/2e17c/images/hugo-logo-wide.svg)

This time, in the year of our lord, 2020 static generators are here, well have been here for a while. You just write in markdown files and it builds those in HTML. You can even mix and match markdown and HTML easily. Jekyll is extremely popular and powers all of those tech-chique GitHub pages. Hugo however, is said to be much faster and powered by Go and as we all know, Go [is so hot right now](https://youtu.be/Jhc6CRgwkqg?t=7). 


I choose a fancy theme called [hello, friend](https://github.com/panr/hugo-theme-hello-friend) - thanks again [Radek](https://twitter.com/panr). Here is the entire source code for my website. To summarize: The workflow goes something like this:

* `hugo new posts/my-post-title-here.md`
* `hugo server -D`, the `-D` flag is important because it will show the draft you are working on!
* Open [localhost:1313](localhost:1313)
* Open `my-post-title-here.md` in your favorite Markdown editor
* Save the file; at every change Hugo will detect the changes and re-render the website

{{< figure src="/img/sweet-setup.png" alt="Hello Friend" position="center" style="border-radius: 8px;" caption="Hello Friend!" captionPosition="center" >}}

This means you can have a nice split-screen setup of your editor of choice next to your browser of choice. Here is an example of my setup: Sublime with Chrome.

## Hosting
As for the hosting, I originally wanted to put it on Google's App Engine. From my experience at Captain AI I really started to enjoy it, and its generous free tier would make it free for any small sized personal website. That brings me to the most important point of this post

**If you are still paying for web-hosting for your personal website, please stop right now. This is definitely not needed anymore in 2020.**

I think App Engine would have been fine to do this, but I felt using a big cloud solution like that for a personal website would be overkill. I also always wanted to use [Netlify](https://netlify.com/), since that seemed like a simple and sleek cloud solution for personal projects. I especially like it's super easy integration with GitHub. Any code push is automatically picked up and run through Hugo. They go very well together! It took a bit to set it all up, but now it's just down to writing Markdown files, and who doesn't love writing Markdown files? It's so ghetto!

So for hosting your website on Netlify you do:

* Register!
* Connect the GitHub repo
* Configure netlify.toml for Hugoyou
* Remove the draft status for each post you want to be visible on your website
* Git commit and push!
* Check build logs
* View your gorgeous website

# run, gerard.run
Oh and the name gerard.run? Well, .sh was my first hope / love (extensions for shell scripts), but some Spanish bastard-o took it! Damn you, Other Gerard and your gorgeous domain name! Let's just say .run files are the hipster versions of .sh files so it's just that much cooler, m'kay? Also I kinda like [running](https://www.strava.com/athletes/23067266).

    
My primary or at least most recent driver for this website was that I wanted to share some of my experience programming in Python, especially with regards to multiprocessing because it seems the resources on it are quite scarce. So you can expect some posts on that first, but who knows, at this point I feel quite eh well shall we say *whimsical*? So who knows what it shall bring us. It could also just be a post filled with meme references / YouTube links.

<!-- Let me know if you have any questions about setting up your own website.  -->


