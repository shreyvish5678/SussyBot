import tensorflow as tf
interpreter = tf.lite.Interpreter(model_path='human_face_generator.tflite')
def handle_response(message) -> str:
    message = message.lower()
    if message == "how":
        return "working"
    elif message == "generate":
        interpreter.allocate_tensors()
        random_noise = tf.random.normal(shape=(1, 100))
        input_tensor = interpreter.tensor(interpreter.get_input_details()[0]['index'])
        input_tensor()[0] = random_noise
        interpreter.invoke()
        generated_output = interpreter.tensor(interpreter.get_output_details()[0]['index'])()[0]
        returned_tensor = tf.cast((generated_output + 1) * 127.5, tf.uint8)
        return returned_tensor
        
        
    