'''
Supporting functions for use in training scripts.
'''

import cPickle as p
import numpy as np
import os

from struct import unpack

top_level_path = os.path.join('..', '..')
MNIST_data_path = os.path.join(top_level_path, 'data')


def get_labeled_data(picklename, b_train=True):
	'''
	Read input-vector (image) and target class (label, 0-9) and return it as 
	a list of tuples.
	'''
	if os.path.isfile('%s.pickle' % picklename):
		data = p.load(open('%s.pickle' % picklename))
	else:
		# Open the images with gzip in read binary mode
		if b_train:
			images = open(os.path.join(MNIST_data_path, 'train-images-idx3-ubyte'), 'rb')
			labels = open(os.path.join(MNIST_data_path, 'train-labels-idx1-ubyte'), 'rb')
		else:
			images = open(os.path.join(MNIST_data_path, 't10k-images-idx3-ubyte'), 'rb')
			labels = open(os.path.join(MNIST_data_path, 't10k-labels-idx1-ubyte'), 'rb')

		# Get metadata for images
		images.read(4)  # skip the magic_number
		number_of_images = unpack('>I', images.read(4))[0]
		rows = unpack('>I', images.read(4))[0]
		cols = unpack('>I', images.read(4))[0]

		# Get metadata for labels
		labels.read(4)  # skip the magic_number
		N = unpack('>I', labels.read(4))[0]

		if number_of_images != N:
			raise Exception('number of labels did not match the number of images')

		# Get the data
		print '...Loading MNIST data from disk.\n'
		x = np.zeros((N, rows, cols), dtype=np.uint8)  # Initialize numpy array
		y = np.zeros((N, 1), dtype=np.uint8)  # Initialize numpy array
		for i in xrange(N):
			if i % 1000 == 0:
				print 'Progress :', i, '/', N
			x[i] = [[unpack('>B', images.read(1))[0] for unused_col in xrange(cols)]  for unused_row in xrange(rows) ]
			y[i] = unpack('>B', labels.read(1))[0]

		print 'Progress :', N, '/', N, '\n'

		data = {'x': x, 'y': y, 'rows': rows, 'cols': cols}
		p.dump(data, open("%s.pickle" % picklename, "wb"))
	
	return data


def is_lattice_connection(sqrt, i, j, lattice_structure):
	'''
	Boolean method which checks if two indices in a network correspond to neighboring nodes in a 4-, 8-, or all-lattice.

	n_e: Square root of the number of nodes in population
	i: First neuron's index
	k: Second neuron's index
	lattice_structure: Connectivity pattern between connected patches
	'''
	if lattice_structure == 'none':
		return False
	if lattice_structure == '4':
		return i + 1 == j and j % sqrt != 0 or i - 1 == j and i % sqrt != 0 or i + sqrt == j or i - sqrt == j
	if lattice_structure == '8':
		return i + 1 == j and j % sqrt != 0 or i - 1 == j and i % sqrt != 0 or i + sqrt == j or i - sqrt == j \
											or i + sqrt == j + 1 and j % sqrt != 0 or i + sqrt == j - 1 and i % sqrt != 0 \
											or i - sqrt == j + 1 and i % sqrt != 0 or i - sqrt == j - 1 and j % sqrt != 0
	if lattice_structure == 'all':
		return True


def save_connections(weights_dir, connections, input_connections, ending):
	'''
	Save all synaptic connection parameters out to disk.
	'''

	# merge two dictionaries of connections into one
	connections.update(input_connections)

	# save out each connection's parameters to disk
	for connection_name in connections.keys():
		print '...Saving connection: ' + os.path.join(weights_dir, connection_name + '_' + ending)
		
		# get parameters of this connection
		connection_matrix = connections[connection_name][:].todense()
		# save it out to disk
		np.save(os.path.join(weights_dir, connection_name + '_' + ending), connection_matrix)


def save_theta(weights_dir, populations, neuron_groups, ending):
	'''
	Save the adaptive threshold parameters out to disk.
	'''

	# iterate over population for which to save theta parameters
	for population in populations:
		# print out saved theta populations
		print '...Saving theta: ' + os.path.join(weights_dir, 'theta_' + population + '_' + ending)

		# save out the theta parameters to file
		np.save(os.path.join(weights_dir, 'theta_' + population + '_' + ending), neuron_groups[population + 'e'].theta)