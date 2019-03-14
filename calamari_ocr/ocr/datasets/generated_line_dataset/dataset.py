from calamari_ocr.ocr.datasets.dataset import DataSet, DataSetMode
from calamari_ocr.proto import TextGeneratorParameters, LineGeneratorParameters
from calamari_ocr.ocr.line_generator import LineGenerator
from calamari_ocr.ocr.text_generation.text_generator import TextGenerator
from multiprocessing import Process, Queue, Manager
import numpy as np
import random
from queue import Empty, Full


class LineGeneratorProcess(Process):
    def __init__(self, output_queue: Queue, text_generator, line_generator, text_only, name=-1):
        super().__init__()
        self.text_generator = TextGenerator(text_generator)
        self.line_generator = LineGenerator(line_generator)
        self.output_queue = output_queue
        self.text_only = text_only
        self.name = "{}".format(name)

    def _handle(self):
        try:
            words = self.text_generator.generate()
            image = self.line_generator.draw(words) if not self.text_only else None
            self.output_queue.put((image, TextGenerator.words_to_unformatted_text(words)), block=True, timeout=1)
        except ValueError as e:
            print(e)
        except Full as e:
            # Full queue
            return

    def run(self):
        random.seed()
        np.random.seed()
        try:
            while True:
                self._handle()
        except (EOFError, BrokenPipeError, ConnectionResetError):
            # queue closed, stop the process
            return


class GeneratedLineDataset(DataSet):
    def __init__(self,
                 mode: DataSetMode,
                 args: dict,
                 ):
        """ Create a dataset from memory
        Since this dataset already contains all data in the memory, this dataset may not be loaded
        Parameters
        ----------
        """
        super().__init__(mode)

        self.loaded = False
        self.lines_per_epoch = 100000
        self._samples = [{'id': '{}'.format(i)} for i in range(self.lines_per_epoch)]
        self.text_generator_params = args.get('text_generator_params', TextGeneratorParameters())
        self.line_generator_params = args.get('line_generator_params', LineGeneratorParameters())
        self.manager = Manager()
        self.data_queue = self.manager.Queue(100)
        self.data_generators = [
            LineGeneratorProcess(
                self.data_queue,
                self.text_generator_params,
                self.line_generator_params,
                False,
                "{}".format(i),
            ) for i in range(8)
        ]
        for d in self.data_generators:
            d.start()

    def __getstate__(self):
        # pickle only relevant information to load samples, drop all irrelevant
        return self.data_queue, self.text_generator_params, self.line_generator_params, self.mode

    def __setstate__(self, state):
        self.data_queue, self.text_generator_params, self.line_generator_params, self.mode = state

    def _load_sample(self, sample, text_only):
        return self.data_queue.get()


if __name__ == "__main__":
    args = dict()

    params = TextGeneratorParameters()
    params.word_length_mean = 11
    params.word_length_sigma = 3
    params.number_of_words_mean = 7
    params.number_of_words_mean = 4
    params.word_separator = " "
    params.sub_script_p = 0.2
    params.super_script_p = 0.2
    params.letter_spacing_p = 0.5
    params.letter_spacing_mean = 0.5
    params.letter_spacing_sigma = 0.05
    params.bold_p = 0.5
    params.italic_p = 0.5
    params.codec.charset.extend(list(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}[]()_-.;:'\""
        "éèíìóòúù"
        "ăȁĕȅĭŏőŭű"
        "āĀǟǞēĒěīĪōŌȫȪūŪǖǕ"
        "ẹḲḳ"
        "αβγδεζηθικλμνξοπρστυφχψω"
        "½"
        "—"
        "–"
        "℔"
        "šŠ"
        "„“"
        "†"
    ))
    args['text_generator_params'] = params

    params = LineGeneratorParameters()
    params.font_size = 48
    params.min_script_offset = -0.5
    params.max_script_offset = 0.5
    params.fonts.extend(['Junicode.ttf', 'DejaVuSerif.ttf'])
    args['line_generator_params'] = params

    dataset = GeneratedLineDataset(DataSetMode.TRAIN, args)

    import matplotlib.pyplot as plt
    line, text = dataset.load_single_sample({}, None)
    print(text)
    plt.imshow(line)
    plt.title(text)
    plt.show()