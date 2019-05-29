from keras.layers import Input, ConvLSTM2D, RNN, Dense, Conv2D, TimeDistributed, Conv2DTranspose
from keras.layers import AveragePooling2D, UpSampling2D
from keras.models import Model, load_model, Sequential
from keras.optimizers import Adam
import numpy as np

from models.keras_model import KerasModel
from models import model_device_adapter

class CnnConvLSTM(KerasModel):
	def __init__(self, gpus=1, batch_size=50, segment_size=12,
		grid_size=100, learning_rate=0.0001, create_tensorboard=False):

		self.segment_size = segment_size

		# Define an input sequence.
		# 1 refers to a single channel of the input
		inputs = Input(shape=(segment_size, grid_size, grid_size, 1))
		
		out = TimeDistributed(Conv2D(32, kernel_size=3, activation='relu'))(inputs)
		out = TimeDistributed(Conv2D(64, kernel_size=3, activation='relu'))(out)
		out = TimeDistributed(AveragePooling2D())(out)
		# 1 filter for the last layer allows the output to have 1 feature map
		# out = TimeDistributed(Conv2D(1, kernel_size=3, activation='relu'))(out)		

		out = ConvLSTM2D(filters=64, kernel_size=5, return_sequences=True, activation='relu')(out)
		out = ConvLSTM2D(filters=64, kernel_size=5, activation='relu')(out)

		out = Conv2DTranspose(64, kernel_size=5, activation='relu')(out)
		out = Conv2DTranspose(64, kernel_size=5, activation='relu')(out)
		out = UpSampling2D()(out)
		out = Conv2DTranspose(32, kernel_size=3, activation='relu')(out)
		out = Conv2DTranspose(1, kernel_size=3, activation='relu')(out)

		self.model = Model(inputs=inputs, outputs=out)
		self.model = model_device_adapter.get_device_specific_model(self.model, gpus)
		
		optimizer = Adam(lr=learning_rate)
		self.model.compile(loss='mse', optimizer=optimizer)

		print(self.model.summary())

		super(CnnConvLSTM, self).__init__(batch_size=batch_size, create_tensorboard=create_tensorboard)

	def form_model_inputs(self, x):
		# (batch_size, segment_size, grid_size, grid_size)
		# print(x.shape)

		# adding an empty (channel) dimension to the end
		return np.expand_dims(x, axis=-1)

	def form_targets(self, y):
		# if data_provider is setup correctly:
		# (batch_size, 1, grid_size, grid_size)
		# print(y.shape)

		assert y.shape[1] == 1, f"expected target segment to be of length 1, got {y.shape[1]}"
		return y[:, 0, :, :, None]

# model = CnnConvLSTM()
# output = model.forward(np.random.randn(1, 12, 100, 100))
# print(output.shape)