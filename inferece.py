# torch
import torch

# init hugging face
from transformers import T5Config, T5Tokenizer, T5ForConditionalGeneration

from eval_utils import compile_fp

class SamplePredictor:
    def __init__(self, model_path, device='cpu', max_len=500, num_beams=1):

        self.max_len = max_len
        self.num_beams = num_beams

        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.model_path = model_path # change path name accordingly
        model_state_dict = torch.load(self.model_path)
        config = T5Config.from_pretrained('t5-small')
        model = T5ForConditionalGeneration(config)
        model.load_state_dict(model_state_dict)
        self.model = model.to(device)

    @staticmethod
    def split_context_program(split):
        program = []
        context = []
        for segment in split[1:]:
            context_track = segment[0] == 'F'
            if context_track:
                context.append(segment)
            else:
                program.append(segment)
        program = '='.join(program[1:])
        context = 'CONTEXT:='+'='.join(context)
        answer = split[0]
        return answer, program, context

    def predict(self, source):
        source = self.tokenizer.batch_encode_plus([source], max_length=800, padding='max_length',return_tensors='pt')
        ids = source['input_ids']
        mask = source['attention_mask']
        generated_ids = self.model.generate(
            input_ids = ids,
            attention_mask = mask,
            max_length=self.max_len,
            num_beams=self.num_beams,
            early_stopping=True
            )
        preds = self.tokenizer.decode(generated_ids.squeeze(), skip_special_tokens=True, clean_up_tokenization_spaces=True)
        answer, program, context = self.split_context_program(preds.split("="))
        return {"question": input_json['question'],
                "direct answer": answer, 
                "context": ';'.join(context.split('=')),
                "program": ';'.join(program.split('='))
                }

if __name__ == '__main__':

    predictor = SamplePredictor()
    question = "How many Mars Bars fit in a room?"
    print("Answering: {}".format(question))
    prediction = predictor.predict(question)
    compiled_answer = compile_fp(prediction['context'], prediction['program'])
    print("Direct Answer is: {}\n Compiled Answer is: {}\n Supporting Facts are: {}\n Program: {}".format(prediction['answer'], compiled_answer, prediction['context'], prediction['program']))
