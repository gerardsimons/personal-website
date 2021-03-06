---
title: "Hello, Friend!"
date: 2020-04-13T22:53:40+02:00
description: "Quarantaine time spent well: my first Hugo-powered personal website"
cover: "img/my-first-post/DSC1143.jpg" 
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

# Hello?
That quote was actually part of the example first post of this website theme, but I liked it, so I kept it. What are you gonna do about? FYI: I can definitely recommend the show as a good way to pass corona time fast and rather funnily. It's also probably the most realistic looking hacking themed TV show / movie I have seen to date. Not that I am much of a hacker - people invariably ask if you are when you are in tech, but just look at all those sweet Linux [terminals](https://www.youtube.com/watch?v=PGjLhOhMLXc). Right? RIGHT?! 

The cover photo is one I took last year on a trip to Scotland with my good friend Georgios. The animal in the picture is not George. George is much hairier. The cow doesn't really have so much to do with this post, but I feel strongly about shaggy beasts livening up websites.

Anywho, let's get down to it. Hello, and welcome all, whoever you may be. Though you are most likely actually just me, constantly re-reading and fretting over potential grammar mistakes. Just like you probably, most of my days are spent cooped, and I was looking for some sort of hobby, and I thought it would **finally** be a good moment to make a website, again.

# Old in Computer Years
Just like dog years, computer years go by fast - real fast, possibly exponentially but at least over 9000. So with 10+ years experience I feel old. Looking back, HTML4 (doesn't it feel like the 5 in HTML is already part of the acronym?), CSS and - sorry for cursing - PHP really got me into web development and excited about the internet as place where you marry technology with design in a very free and personal way. Then came the JavaScript, the jQuery and now there's a new front-end framework every year, which was all very offputting to me. The last time I made a personal website, was just a very bare HTML placeholder that said "under construction" for its entire measley existence. Before even that, I am pretty sure I still used that giant [LAMP](https://en.wikipedia.org/wiki/LAMP_(software_bundle)) stack with MySQL, PHP and the likes, including paid hosting and clumsy FTP servers. Ah, the good old days.

## Staying Young with Hugo

![Image](https://d33wubrfki0l68.cloudfront.net/c38c7334cc3f23585738e40334284fddcaf03d5e/2e17c/images/hugo-logo-wide.svg)

So what do you do if you feel old? You get a hot new girlfriend! Or in the case of social distancing you just get a new website. This time around though, things would be different. Static generators are here, well have been here for a while, actually. I had been oggling them for a while, but only now decided it was time. And I love it. After some setting up, all you do is write in markdown files and it turns those into HTML. You can even mix and match markdown and HTML. 

A bit of background on generators: [Jekyll](https://jekyllrb.com/) is extremely popular and powers GitHub pages. Hugo however, is said to be much faster and powered by Go and as we all know, Go [is so hot right now](https://youtu.be/Jhc6CRgwkqg?t=7). So having decided on that, I also choose a fancy theme to go along with it, called [hello, friend](https://github.com/panr/hugo-theme-hello-friend) - thanks again [Radek](https://twitter.com/panr). 

Just to give you an idea, here is the workflow in Hugo, heavily simplified

* `hugo new site personal-website`
* `hugo new posts/my-post-title-here.md`
* `hugo server -D`, the `-D` flag is important because it will show the draft you are working on!
* Open [localhost:1313](localhost:1313)
* Open `my-post-title-here.md` in your favorite Markdown editor
* Save the file; at every change Hugo will detect the changes and re-render the website

{{< figure src="/img/my-first-post/sweet-setup.png" alt="Hello Friend" position="center" style="border-radius: 8px;" caption="Hello Friend!" captionPosition="center" >}}

This means you can have a nice split-screen setup of your editor of choice next to your browser of choice. Here is an example of my setup: Sublime with Chrome.

And since Hugo is geared towards developers, you get some sweet syntax highlighting for your Markdown code snippets. Here's an example of Google's PageRank algorithm in Python:

```python
import numpy as np

def pagerank(M, num_iterations=100, d=0.85):
    N = M.shape[1]
    v = np.random.rand(N, 1)
    v = v / np.linalg.norm(v, 1)
    iteration = 0
    while iteration < num_iterations:
        iteration += 1
        v = d * np.matmul(M, v) + (1 - d) / N
    return v
```


## Hosting
As for the hosting,  That brings me to the most important point of this post:

**Stop paying for web hosting!** This is almost certainly not necesary anymore in 2020 for small personal websites.

Keeping that in mind I originally wanted to put it on [Google's App Engine](https://cloud.google.com/appengine/). which from my experience at Captain AI I really started to enjoy. Its generous free tier would make it free for sure, but I felt a big cloud solution to be a bit of an overkill for website with some animal pictures :). Also, I really wanted to try [Netlify](https://netlify.com/), which seemed like a much more simple and sleek cloud solution for personal projects. I especially enjoyed it's super straightforward integration with GitHub. Any code push is automatically picked up, and run through Hugo. This continuous build cycle is not uncommon these days but was particularly simple to set up in this case.

Also, Hugo and Netlify go very well together! It took a bit to set it all up, but now it's just down to writing Markdown files, and who doesn't love writing Markdown files? It's so ghetto!

So for hosting your website on Netlify you do:

* Register!
* Connect the GitHub repo that contains your code
* Configure netlify.toml for Hugo
* Remove the draft status for each post you want to be visible on your website
* Git commit and push!
* Check build logs
* Be amazed or you know, appalled, by your creation

{{< figure src="/img/my-first-post/netlify.png" alt="Netlify Dashboard" position="center" style="border-radius: 8px;" caption="Netlify Deployments and my useful git commit messages" captionPosition="center" >}}

# run, gerard.run
Oh and the name gerard.run? Well, .sh was my first hope / love. It's the file extension for shell scripts, but [some Spanish bastard-o](https://gerard.sh/about) took it! Damn you, Gerardo and your terrific domain name. Occasionally though you also have .run files. Let's just say they are the hipster versions of .sh files so it's just that much cooler? Also I kinda like [running](https://www.strava.com/athletes/23067266).

My primary, or at least most recent driver for this website however, was that I wanted to share some of my experience programming in Python for [Captain AI](https://captainai.com/), especially with regards to multiprocessing because it seems the resources on it are limited. So you can probably expect some posts on that first, but who knows, at this point I feel quite eh well shall we say *whimsical* so this whole website could also just turn out to be another memes website. 

Stay tuned, and post a comment below!

