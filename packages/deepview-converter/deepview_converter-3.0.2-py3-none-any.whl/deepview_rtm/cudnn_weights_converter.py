# Copyright 2018 by Au-Zone Technologies.  All Rights Reserved.
#
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential.
#
# This source code is provided solely for runtime interpretation by Python.
# Modifying or copying any source code is explicitly forbidden.

import numpy as np
"""

        Cudnn compatible GRU (from Cudnn library user guide):
            # reset gate
            r_t = sigma(x_t * init_w_r + h_t-1 * R_r + b_{Wr} + b_{Rr}) 
             # update gate
            u_t = sigma(x_t * W_u + h_t-1 * R_u + b_{Wu} + b_{Ru})
            # new memory gate
            h'_t = tanh(x_t * W_h + r_t .* (h_t-1 * R_h + b_{Rh}) + b_{Wh})
            h_t = (1 - u_t) .* h'_t + u_t .* h_t-1

        Other GRU (tf.nn.rnn_cell.GRUCell and tf.contrib.rnn.GRUBlockCell):            
            # new memory gate
            (h'_t = tanh(x_t * W_h + (r_t .* h_t-1) * R_h + b_{Wh}))
        Which is not equivalent to Cudnn GRU: in addition to the extra bias term b_Rh,
            (r .* (h * R) != (r .* h) * R)

        Weights and biases used: 
             self._gate_kernel                          w_ir
             self._gate_bias                            b_ir
             self._candidate_input_kernel               w_h
         self._candidate_hidden_kernel                  r_h
             self._candidate_input_bias                 b_wh  
             self._candidate_hidden_bias                b_rh    

"""

class GRUWeightsConverter():
    def __init__(self, input_size, num_units):
        self._input_size = input_size
        self._num_units = num_units

    def _tf_to_cudnn_biases(self, *tf_biases):
        b_ir, b_wh, b_rh = tf_biases
        bi, br = b_ir * 0.5, b_ir * 0.5
        b_wi, b_wr = np.split(bi, 2, axis=0)
        b_ri, b_rr = np.split(br, 2, axis=0)
        return b_wi, b_wr, b_wh, b_ri, b_rr, b_rh

    def _tf_to_cudnn_weights(self, *tf_weights):
        input_size = self._input_size

        w_ir, w_h, r_h = tf_weights
        w_ir = np.transpose(w_ir)
        w_h = np.transpose(w_h)
        r_h = np.transpose(r_h)

        init_w_i, init_w_r = np.split(w_ir, 2, axis=0)
        w_i, r_i = np.split(init_w_i, [input_size], axis=1)
        w_r, r_r = np.split(init_w_r, [input_size], axis=1)

        return w_i, w_r, w_h, r_i, r_r, r_h

    def _cudnn_to_tf_weights(self, *cu_weights):
        w_i, w_r, w_h, r_i, r_r, r_h = cu_weights
        init_w_i = np.concatenate((w_i, r_i), axis=1)
        init_w_r = np.concatenate((w_r, r_r), axis=1)

        return (np.transpose(np.concatenate((init_w_i, init_w_r), axis=0)),
                np.transpose(w_h), np.transpose(r_h))

    def _cudnn_to_tf_biases(self, *biases):
        r"""Stitching cudnn canonical biases to generate tf canonical biases."""
        b_wi, b_wr, b_wh, b_ri, b_rr, b_rh = biases
        return (
            # Save only the sum instead of individual biases. When recovering,
            # return two biases each with half the value. Since RNN does not
            # regularize by weight decay, it has no side effect in training or
            # inference.
            np.concatenate((b_wi, b_wr), axis=0) + np.concatenate((b_ri, b_rr), axis=0),b_wh,b_rh)



    def convert_cudnn_to_tf(self, weights_biases):
        cudnn_weights = (weights_biases['cudnn_w_i'],   #16,2
                        weights_biases['cudnn_w_r'],    #16,2
                        weights_biases['cudnn_w_h'],    #16,2
                        weights_biases['cudnn_r_i'],    #16,16
                        weights_biases['cudnn_r_r'],    #16,16
                        weights_biases['cudnn_r_h'])    #16,16
        cudnn_biases = (weights_biases['cudnn_b_wi'],   #16
                        weights_biases['cudnn_b_wr'],   #16
                        weights_biases['cudnn_b_wh'],   #16
                        weights_biases['cudnn_b_ri'],   #16
                        weights_biases['cudnn_b_rr'],   #16
                        weights_biases['cudnn_b_rh'])   #16

        w_ir, w_h, r_h = self._cudnn_to_tf_weights(*cudnn_weights)
        b_ir, b_wh, b_rh = self._cudnn_to_tf_biases(*cudnn_biases)

        tf_weights_biases = {"w_ir":w_ir,
                             "w_h":w_h,
                             "r_h":r_h,
                             "b_ir":b_ir,
                             "b_wh":b_wh,
                             "b_rh":b_rh}
        return tf_weights_biases

    def convert_cudnn_memblob_to_tf(self, cudnn_mem_blob, nb_units, input_depth):

        cudnn_weights_flatten, cudnn_biases_flatten = np.split(cudnn_mem_blob, [cudnn_mem_blob.size-nb_units*6], axis=0)
        x = nb_units*input_depth
        y = nb_units * nb_units
        z = nb_units
        w_i, w_r, w_h, r_i, r_r, r_h = np.split(cudnn_weights_flatten, [x,2*x,3*x,3*x+y,3*x+2*y], axis=0)
        b_wi, b_wr, b_wh, b_ri, b_rr, b_rh = np.split(cudnn_biases_flatten, [z,2*z,3*z,4*z,5*z], axis=0)

        w_i = np.reshape(w_i, [nb_units,input_depth])
        w_r = np.reshape(w_r, [nb_units,input_depth])
        w_h = np.reshape(w_h, [nb_units,input_depth])
        r_i = np.reshape(r_i, [nb_units,nb_units])
        r_r = np.reshape(r_r, [nb_units,nb_units])
        r_h = np.reshape(r_h, [nb_units,nb_units])

        cudnn_weights = (w_i, w_r, w_h, r_i, r_r, r_h)
        cudnn_biases = (b_wi, b_wr, b_wh, b_ri, b_rr, b_rh)

        w_ir, w_h, r_h = self._cudnn_to_tf_weights(*cudnn_weights)
        b_ir, b_wh, b_rh = self._cudnn_to_tf_biases(*cudnn_biases)

        tf_weights_biases = {"w_ir":w_ir,
                             "w_h":w_h,
                             "r_h":r_h,
                             "b_ir":b_ir,
                             "b_wh":b_wh,
                             "b_rh":b_rh}

        return tf_weights_biases

    def convert_tf_to_cudnn(self, tensors):
        cu_weights, cu_biases = [], []

        layer_weights = (tensors['w_ir'], tensors['w_h'], tensors['r_h'])
        cu_weights.extend(self._tf_to_cudnn_weights(*layer_weights))

        layer_biases = (tensors['b_ir'], tensors['b_wh'], tensors['b_rh'])
        cu_biases.extend(self._tf_to_cudnn_biases(*layer_biases))
        return cu_weights, cu_biases

"""
        Weights and biases used: 
            gate_kernel                          w_ir
            gate_bias                            b_ir
            candidate_input_kernel               w_h
            candidate_hidden_kernel              r_h
            candidate_input_bias                 b_wh  
            candidate_hidden_bias                b_rh  
"""
