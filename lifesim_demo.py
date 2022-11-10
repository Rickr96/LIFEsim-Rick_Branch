import requests

import lifesim

# ---------- Set-Up ----------

# create bus
bus = lifesim.Bus()

# setting the options
bus.data.options.set_scenario('baseline')

# set options manually
bus.data.options.set_manual(diameter=4.)

# ---------- Downloading the P-Pop catalog ----------

data = requests.get('https://raw.githubusercontent.com/kammerje/P-pop/main/TestPlanetPopulation.txt')

with open('C:\Work\MSA\LIFEsim-Rick_Branch/ppop_catalog.txt', 'wb') as file:
    file.write(data.content)

# ---------- Loading the Catalog ----------

bus.data.catalog_from_ppop(input_path='C:\Work\MSA\LIFEsim-Rick_Branch/ppop_catalog.txt')
bus.data.catalog_remove_distance(stype=0, mode='larger', dist=0.)  # remove all A stars
bus.data.catalog_remove_distance(stype=4, mode='larger', dist=10.)  # remove M stars > 10pc to
# speed up calculation

# ---------- Creating the Instrument ----------

# create modules and add to bus
instrument = lifesim.Instrument(name='inst')
bus.add_module(instrument)
# TransmissionMap is the "normal" transmission mode without planet movement.
# It is mutually exclusive with OrbitalTransmissionMap

#orb_transm = lifesim.TransmissionMap(name='transm')

# OrbitalTransmissionMap is including planet movement.
# It is mutually exclusive with TransmissionMap

orb_transm = lifesim.OrbitalTransmissionMap(name='orb_transm')
bus.add_module(orb_transm)

exo = lifesim.PhotonNoiseExozodi(name='exo')
bus.add_module(exo)
local = lifesim.PhotonNoiseLocalzodi(name='local')
bus.add_module(local)
star = lifesim.PhotonNoiseStar(name='star')
bus.add_module(star)

# connect all modules
bus.connect(('inst', 'orb_transm'))
bus.connect(('inst', 'exo'))
bus.connect(('inst', 'local'))
bus.connect(('inst', 'star'))

bus.connect(('star', 'orb_transm'))

# ---------- Creating the Optimizer ----------
# After every planet is given an SNR, we want to distribute the time available in the search phase
# such that we maximize the number of detections.

# optimizing the result
opt = lifesim.Optimizer(name='opt')
bus.add_module(opt)
ahgs = lifesim.AhgsModule(name='ahgs')
bus.add_module(ahgs)

bus.connect(('orb_transm', 'opt'))
bus.connect(('inst', 'opt'))
bus.connect(('opt', 'ahgs'))

# ---------- Running the Simulation ----------

# run simulation. This function assigns every planet an SNR for 1 hour of integration time. Since
# we are currently only simulating photon noise, the SNR will scale with the integration time as
# sqrt(t)
instrument.get_snr()

opt.ahgs()

# ---------- Saving the Results ----------

bus.data.export_catalog(output_path='C:\Work\MSA\LIFEsim-Rick_Branch/PM_and_LZ_ON.hdf5')


# ---------- Reading the Results ----------
# import a previously saved catalog
"""
bus_read = lifesim.Bus()
bus_read.data.options.set_scenario('baseline')
bus_read.data.import_catalog(input_path='C:\Work\MSA\LIFEsim-Rick_Branch/demo1.hdf5')
"""