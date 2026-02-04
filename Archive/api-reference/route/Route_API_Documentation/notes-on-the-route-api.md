# Additional Notes from Aidan about the API

The security is actually a bit fiddly to setup but you'll only have to do this once. You need a username and password, which generates a header. You'll also need an API key.

The MediaTel API has different endpoints depending on whether you want information concerning frames, or demographics, or impacts etc. These provide logical splits for both the developer and the client.

When you call these endpoints, you normally make a **request**. Again, rest-ful APIs normally adhere to a few simple types of request: GET, POST, DELETE, ADD. These are all quite self-explanatory.

**We will use POST for everything.** This is because it is (ever-so-slightly) more secure. It is more secure as GET parameters are passed via URL. So they are stored in server logs and browser history. See [here](https://stackoverflow.com/questions/198462/is-either-get-or-post-more-secure-than-the-other) for more info.

You can make a request in a number of ways. For quick and easy stuff you can use the curl program on your terminal. There are also websites dedicated to easy requests like [postman.](https://www.postman.com/) All programming languages will have frameworks setup to make requests to APIs. The most common one in Python is `requests`. I use `aiohttp` as well, as I like to do things asynchronously.

We'll go through a couple of functions to call some data now.

Then there's typical Python error-handling, re-trying etc.

The onus is on you using the REST API to know what to expect. The documentation should show you the format of the response that you'll get as well as any errors to expect.

The rate limits are 6-calls a second ish.

#### Other Notes:

* Whatever you creates/develops please keep in mind reusability, please spend the additional time to follow software dev best practice i.e., modularity, use functions/methods, create libraries, make things a generalised as possible, clear documentation, pass variables/config don't hard code. Note this takes longer than quickly getting the job done but has benefits in the long run
* Keep an eye on creating tools that can be used by others in the long run
* Please also create a separate that describes what your code does and what it is for, I am not a fan of my code does the documentation. Include the appropriate amount of documentation in the code, but not unnecessary documentation within the code. Provide a readme on GitHub, but also create on Outline overarching documentation, which repos do what, how they are used what they are for, with a short description of each
* Route doesn't have a concept of a year, all we have is an average week in a year and the data is expanded from there
* The reason for linear impacts is the source count data for example road counts (AADF - annual average daily flow), everything essentially boils down to weekly counts, that can be expanded up or broken down by the day
* When looking at the counts for a specific target this relies on the underlying sample data, things can get weird if you don't have enough sample
* Digital frames (when running a spot schedule) again use the sample data to work out the impacts
* I don't use the granularity function, things get weird counterintuitive, I've never found a need for it
* Every campaign should have the month passed to it, having an OOH campaign that doesn't reflect the daylight factors/seasonality makes no logical sense. I use March as a standard month as it is a good medium between the darkest month (Jan) and the one with the most daylight
* **Reach can result in counterintuitive results, due to being a calculation based on the probabilities. In some instances adding more frames to an already high reaching campaign can result in a slight reduction in reach.** Really there is no change in the reach but a change in the available data which goes into the calculation, an edge case but can happen.
* Try to design your API calls to be done in as parallel a way possible, this will cut down on processing time, avoid iterating through lists if you can, Python doesn't have this natively but can be done, you may want to explore using Go, but up to you, get the job done!
* To get out data for individual frames you can use the grouping API method, a sweet spot is to call up to 10k in a single call, this really benefits from making parallel calls to get lots of data back. You can pass the impacts only option to the API making the call more responsive