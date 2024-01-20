import tensorflow as tf
import json
interpreter = tf.lite.Interpreter(model_path='human_face_generator.tflite')

def handle_response(message) -> str:
    message = message.lower()
    if message == "generate":
        interpreter.allocate_tensors()
        random_noise = tf.random.normal(shape=(1, 100))
        input_tensor = interpreter.tensor(interpreter.get_input_details()[0]['index'])
        input_tensor()[0] = random_noise
        interpreter.invoke()
        generated_output = interpreter.tensor(interpreter.get_output_details()[0]['index'])()[0]
        returned_tensor = tf.cast((generated_output + 1) * 127.5, tf.uint8)
        return {"image": returned_tensor, "noise": random_noise}
    elif message == "board":
        with open("user.json", "r") as file:
            user_data = json.load(file)
            sorted_data = dict(sorted(user_data.items(), key=lambda x: x[1], reverse=True))
        val = 0
        string = ""
        for key, value in sorted_data.items():
            val += 1
            string += f"`{val}. {key}: {value}`\n"
            if val == 10:
                break
        return string
    