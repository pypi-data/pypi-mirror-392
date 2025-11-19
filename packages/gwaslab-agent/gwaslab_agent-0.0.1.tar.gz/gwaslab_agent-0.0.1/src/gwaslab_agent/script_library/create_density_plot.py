# get_density, plot_snp_density
import gwaslab as gl

sumstats = gl.Sumstats("mysumstats.txt.gz", fmt="auto")

sumstats.get_density()

sumstats.plot_snp_density()