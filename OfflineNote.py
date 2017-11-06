import sys
sys.path.append("/usr/local/lib/python2.7/site-packages")
sys.path.append("/Library/Python/2.7/site-packages")

from Tkinter import *

import essentia
from essentia.standard import *

import math
import numpy as np
from scipy import signal

import sklearn
from sklearn.mixture import GMM, BayesianGaussianMixture, DPGMM, VBGMM, GaussianMixture

from ctypes import *

ll = cdll.LoadLibrary
lib = ll('./libpycall.so')

class OfflineNote:
    parent = None

    def __init__(self, p):
        self.parent = p

    # k = 2, Q = 10, 1 .. 10, d1 = C2 - C1, d2 = C3 - C2, d9 =
    def get_delta(self, mfcc_list):
        m = []
        length = len(mfcc_list)
        for i in range(0, length):
            if i == 0 or i == 1:
                continue
                #m.append(mfcc_list[i + 1] - mfcc_list[i])
            elif i == length - 1 or i == length - 2:
                continue
                #m.append(mfcc_list[i] - mfcc_list[i - 1])
            else:
                temp = -2 * mfcc_list[i - 2] - mfcc_list[i - 1] + mfcc_list[i + 1] + 2 * mfcc_list[i + 2]
                temp = temp / math.sqrt(10.0)
                m.append(temp)

        return m

    def get_MFCC_0(self, audio):
        w = Windowing(type='hamming')
        spectrum = Spectrum()
        saudio = spectrum(w(audio))
        mfcc = MFCC(inputSize=len(saudio), numberCoefficients=13)  # highFrequencyBound = 8000, numberBands = 26)

        mfcc_bands, mfcc_coeffs = mfcc(saudio)

        return mfcc_coeffs.tolist()

    def get_MFCC_1(self, audio):
        w = Windowing(type='hamming')
        spectrum = Spectrum()
        saudio = spectrum(w(audio))
        # mfcc = MFCC(inputSize = len(saudio), numberCoefficients = 15, highFrequencyBound = 6000)

        mfcc = MFCC(inputSize=len(saudio), numberCoefficients=13)  # highFrequencyBound = 8000, numberBands = 26)

        first_delta = []
        mfcc_bands, mfcc_coeffs = mfcc(saudio)
        first_delta = self.get_delta(mfcc_coeffs)
        mfcc_coeffs = mfcc_coeffs.tolist() + first_delta
        # second_delta = self.get_delta(first_delta)
        # mfcc_coeffs = mfcc_coeffs + second_delta

        return mfcc_coeffs

    def get_MFCC_2(self, audio):
        w = Windowing(type='hamming')
        spectrum = Spectrum()
        saudio = spectrum(w(audio))
        mfcc = MFCC(inputSize=len(saudio), numberCoefficients=13)  # highFrequencyBound = 8000, numberBands = 26)

        first_delta = []
        second_delta = []

        mfcc_bands, mfcc_coeffs = mfcc(saudio)
        mfcc_coeffs = mfcc_coeffs.tolist()
        first_delta = self.get_delta(mfcc_coeffs)
        mfcc_coeffs = mfcc_coeffs + first_delta
        second_delta = self.get_delta(first_delta)
        mfcc_coeffs = mfcc_coeffs + second_delta

        return mfcc_coeffs

    def handler(self, path, person_num):
        audio = MonoLoader(filename=path, sampleRate=16000)()

        newaudio = []
        feature_list = []
        listaudio = audio.tolist()
        audio_list = []
        i = 0

        num = 0
        temprecord = []

        isLast = False
        print("start feature")

        for frame in FrameGenerator(audio):
            c = SilenceRate(thresholds=[0.0005])(frame)
            if c <= 0.5:
                flag = False
                if num <= 20 and len(temprecord) != 0:
                    if len(audio_list) != 0:
                        newaudio = newaudio + temprecord
                        flag = True

                if isLast or flag:
                    newaudio = newaudio + listaudio[(512 * i + 512):(512 * i + 1024)]
                else:
                    newaudio = newaudio + listaudio[(512 * i):(512 * i + 1024)]

                num = 0
                temprecord = []
                isLast = True
            else:
                num = num + 1

                temprecord = temprecord + listaudio[(512 * i + 512):(512 * i + 1024)]
                isLast = False

                if num == 21:
                    if len(newaudio) >= 8000:
                        audio_list.append(newaudio)
                    newaudio = []

            i = i + 1

        if len(newaudio) >= 8000:
            audio_list.append(newaudio)

        output = []
        feature_list = []

        maxIns = -np.inf
        maxZCR = -np.inf
        maxHFC = -np.inf

        print("finish feature")
        print(len(audio_list))

        for i in range(0, len(audio_list)):
            currentZCR = 0
            currentIns = 0
            currentHFC = 0

	    if len(audio_list[i]) % 2 == 1:
		audio_list[i] = audio_list[i] + [0]

            eout = essentia.array(audio_list[i])
            feature_list.append(self.get_MFCC_1(eout))

            currentZCR = ZeroCrossingRate()(eout)
            currentZCR = math.log(currentZCR)
            currentIns = InstantPower()(eout)
            currentIns = math.log(currentIns)
            currentHFC = HFC()(eout)
            currentHFC = math.log(currentHFC)

            if currentZCR > maxZCR:
                maxZCR = currentZCR

            if currentIns > maxIns:
                maxIns = currentIns

            if currentHFC > maxHFC:
                maxHFC = currentHFC

            feature_list[-1][0] = currentZCR
            feature_list[-1][1] = currentIns
            feature_list[-1].append(currentHFC)

        for k in feature_list:
            k[0] = k[0] - maxZCR
            k[1] = k[1] - maxIns
            k[-1] = k[-1] - maxHFC

        # g = VBGMM(n_components = 20, covariance_type = 'tied', alpha = 2.0 / math.log(len(feature_list)))
        # g = BayesianGaussianMixture(n_components = 8, covariance_type = 'tied', weight_concentration_prior_type='dirichlet_process',  weight_concentration_prior = 2.0 / math.log(len(feature_list)))
        # g = BayesianGaussianMixture(n_components=10, covariance_type='full', weight_concentration_prior= 2.0 / math.log(len(feature_list)), weight_concentration_prior_type='dirichlet_process', mean_precision_prior=1e-2, init_params="random", max_iter=100, random_state=2)
        #best_g = GaussianMixture(n_components=128, covariance_type='tied')

        if person_num == 0:
            lowest_bic = np.infty
            array_feature = np.array(feature_list)
            bestnum = 0

            for cov_type in ['full', 'tied', 'diag', 'spherical']:
                for num in range(2, min(len(feature_list), 10)):
                    g = GaussianMixture(n_components = num, covariance_type = cov_type)
                    g.fit(feature_list)
                    newbic = g.bic(array_feature)
                    print newbic
                    if newbic < lowest_bic:
                        lowest_bic = newbic
                        best_g = g
                        bestnum = num

            g = best_g
            print(bestnum)
        else:
            g = GaussianMixture(n_components = person_num, covariance_type = 'tied')
            g.fit(feature_list)

        # print(len(feature_list))


        print("finish GMM")

        last = -1
        answer_list = []

        counter = 1
        namedict = {}
        typelist = []

        for i in range(0, len(feature_list)):
            newindex = g.predict([feature_list[i]])[0]

            if newindex == last:
                answer_list[-1] = answer_list[-1] + audio_list[i]
            else:
                print(newindex)
                last = newindex
                answer_list.append(audio_list[i])

                if not namedict.has_key(newindex):
                    namedict[newindex] = counter
                    counter = counter + 1

                typelist.append(namedict[newindex])

	print(len(answer_list))

        for j in range(0, len(answer_list)):
            oname = "offlinetemp.wav"
            MonoWriter(filename=oname, sampleRate=16000)(essentia.array(answer_list[j]))
            c_pBuf = create_string_buffer('', 100000)
            lib.process(oname, c_pBuf)
            data = string_at(c_pBuf)
            s = "Talker " + str(typelist[j]) + ": " + data
            print(s)
            self.writeToOutput(s)
        

    def writeToOutput(self, input):
        self.parent.outputText.insert(END, input + '\n')
	self.parent.master.update()
