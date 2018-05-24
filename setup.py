from setuptools import setup, find_packages

setup(
    name='calamari_ocr',
    version='0.1.6',
    packages=find_packages(),
    license='GPL-v3.0',
    long_description=open("README.md").read(),
    include_package_data=True,
    author="Christoph Wick",
    author_email="christoph.wick@informatik.uni-wuerzburg.de",
    url="http://github.com/chwick/calamari",
    download_url='https://github.com/ChWick/calamari/archive/v0.1.6.tar.gz',
    entry_points={
        'console_scripts': [
            'calamari-eval=calamari_ocr.scripts.eval:main',
            'calamari-predict=calamari_ocr.scripts.predict:main',
            'calamari-resume-training=calamari_ocr.scripts.resume_training:main',
            'calamari-train=calamari_ocr.scripts.train:main',
            'calamari-cross-fold-train=calamari_ocr.scripts.cross_fold_train:main',
            'calamari-pred_to_json=calamari_ocr.scripts.cross_fold_train:main',
        ],
    },
    install_requires=open("requirements.txt").read().split(),
    keywords=['OCR', 'optical character recognition', 'ocropy', 'ocropus', 'kraken'],
    data_files=[('', ["requirements.txt"])],
)
