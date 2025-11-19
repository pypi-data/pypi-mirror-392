#methods: plot_mqq, plot_manhattan

# Load sumstats

sumstats = gl.Sumstats("mysumstats.txt.gz", fmt="auto")

# run basic_check if necessary

# plot 

sumstats.plot_mqq(skip = 2)