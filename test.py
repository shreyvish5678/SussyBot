import tensorflow as tf
import matplotlib.pyplot as plt
interpreter = tf.lite.Interpreter(model_path='human_face_generator.tflite')
interpreter.allocate_tensors()
random_noise = tf.random.normal(shape=(1, 100))
input_tensor = interpreter.tensor(interpreter.get_input_details()[0]['index'])
input_tensor()[0] = random_noise
interpreter.invoke()
generated_output = interpreter.tensor(interpreter.get_output_details()[0]['index'])()[0]
plt.imshow(generated_output*0.5+0.5)
plt.show()