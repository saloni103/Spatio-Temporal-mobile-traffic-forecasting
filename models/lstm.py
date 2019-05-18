from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, CuDNNLSTM
from tensorflow.keras.layers import LSTM as CpuLSTM
from tensorflow.test import is_gpu_available
from models.losses import nrmse_keras as nrmse
from models.model import Model

class LSTM(Model):

	def __init__(self, batch_size, segment_size, num_features, hidden_size=100):
		self.model = Sequential()
		if is_gpu_available():
			print("\nUsing CuDNNLSTM!\n")
			self.model.add(CuDNNLSTM(hidden_size))
		else:
			print("\nUsing CPU LSTM!\n")
			self.model.add(CpuLSTM(hidden_size))
		self.model.add(Dense(1))
		self.model.compile(loss=nrmse, optimizer='adam')

		self.batch_size = batch_size

	def reshape_inputs(self, x):
		return x.reshape(x.shape[0], x.shape[1], x.shape[2] * x.shape[3])

	def forward(self, x):
		x_reshaped = self.reshape_inputs(x)
		return self.model.predict(x_reshaped, batch_size=self.batch_size)

	def train(self, x, y):
		""" inputs:
				x - (batch_size, segment_size, window_width, window_height)
				y - (batch_size,)
		"""		

		x_reshaped = self.reshape_inputs(x)
		history = self.model.fit(x_reshaped, y, batch_size=self.batch_size, epochs=1)		
		return history.history["loss"][0]

	def evaluate(self, x, y):
		x_reshaped = self.reshape_inputs(x)
		return self.model.evaluate(x_reshaped, y, batch_size=y.shape[0])