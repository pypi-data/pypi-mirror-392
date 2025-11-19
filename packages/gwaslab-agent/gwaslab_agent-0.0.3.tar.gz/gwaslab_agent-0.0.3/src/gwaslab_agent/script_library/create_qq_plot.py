#methods: plot_qq

import gwaslab as gl
# Load sumstats

sumstats = gl.Sumstats("mysumstats.txt.gz", fmt="auto")

# run basic_check if necessary

# QQ plot 
sumstats.plot_qq()

# maf-stratified QQ plot 
sumstats.plot_qq(stratified=True)