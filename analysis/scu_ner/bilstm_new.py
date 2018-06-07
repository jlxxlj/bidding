# -*- coding: utf-8 -*-
"""
Created on Fri May 06 14:44:55 2016

@author: CJQ
"""

import cPickle
import numpy as np
from collections import defaultdict, OrderedDict
import theano
import theano.tensor as T
import warnings
import time
import numpy
import theano.tensor as tensor
from theano import config
import six.moves.cPickle as pickle
import theano
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams

# import ipdb

import copy

import os

from bilstm_data_new import load_data, prepare_data

# theano.config.compute_test_value = 'off'

# THEANO_FLAGS = 'exception_verbosity=high'

SEED = 123
numpy.random.seed(SEED)

profile = False

layers = {'ff': ('param_init_fflayer', 'fflayer'),
          'gru': ('param_init_gru', 'gru_layer'),
          'lstm': ('param_init_lstm', 'lstm_layer'),
          'cnn': ('param_init_cnn', 'cnn_layer'),
          }


def get_layer(name):
    fns = layers[name]
    return (eval(fns[0]), eval(fns[1]))


def numpy_floatX(data):
    return numpy.asarray(data, dtype=config.floatX)


def tanh(x):
    return tensor.tanh(x)


# get the list of parameters: Note that tparams must be OrderedDict
def itemlist(tparams):
    return [vv for kk, vv in tparams.iteritems()]


def ortho_weight(ndim):
    W = numpy.random.randn(ndim, ndim)
    u, s, v = numpy.linalg.svd(W)
    return u.astype(config.floatX)


def norm_weight(nin, nout=None, scale=0.1, ortho=True, win=1):
    if nout is None:
        nout = nin
    if win == 1:
        if nout == nin and ortho:
            W = ortho_weight(nin)
        else:
            W = scale * numpy.random.randn(nin, nout)
    else:
        W = scale * numpy.random.randn(win, nin, nout)
    return W.astype(config.floatX)


# make prefix-appended name
def _p(pp, name):
    return '%s_%s' % (pp, name)


def unzip(zipped):
    """
    When we pickle the model. Needed for the GPU stuff.
    """
    new_params = OrderedDict()
    for kk, vv in zipped.items():
        new_params[kk] = vv.get_value()
    return new_params


def get_minibatches_idx(n, minibatch_size, shuffle=False):
    """
    Used to shuffle the dataset at each iteration.
    """

    idx_list = numpy.arange(n, dtype="int32")

    if shuffle:
        numpy.random.shuffle(idx_list)

    minibatches = []
    minibatch_start = 0
    for i in range(n // minibatch_size):
        minibatches.append(idx_list[minibatch_start:
        minibatch_start + minibatch_size])
        minibatch_start += minibatch_size

    if (minibatch_start != n):
        # Make a minibatch out of what is left
        minibatches.append(idx_list[minibatch_start:])

    return zip(range(len(minibatches)), minibatches)


def zipp(params, tparams):
    """
    When we reload the model. Needed for the GPU stuff.
    """
    for kk, vv in params.items():
        tparams[kk].set_value(vv)


# dropout
def dropout_layer(state_before, use_noise, trng):
    proj = tensor.switch(
        use_noise,
        state_before * trng.binomial(state_before.shape, p=0.5, n=1,
                                     dtype=state_before.dtype),
        state_before * 0.5)
    return proj


def init_tparams(params):
    tparams = OrderedDict()
    for kk, pp in params.iteritems():
        tparams[kk] = theano.shared(params[kk], name=kk)
    return tparams


# load parameters
def load_params(path, params):
    pp = numpy.load(path)
    for kk, vv in params.iteritems():
        if kk not in pp:
            warnings.warn('%s is not in the archive' % kk)
            continue
        params[kk] = pp[kk]

    return params


def sgd(lr, tparams, grads, x, mask, y, cost):
    """ Stochastic Gradient Descent

    :note: A more complicated version of sgd then needed.  This is
        done like that for adadelta and rmsprop.

    """
    # New set of shared variable that will contain the gradient
    # for a mini-batch.
    gshared = [theano.shared(p.get_value() * 0., name='%s_grad' % k)
               for k, p in tparams.items()]
    gsup = [(gs, g) for gs, g in zip(gshared, grads)]

    # Function that computes gradients for a mini-batch, but do not
    # updates the weights.
    f_grad_shared = theano.function([x, mask, y], cost, updates=gsup,
                                    name='sgd_f_grad_shared')

    pup = [(p, p - lr * g) for p, g in zip(tparams.values(), gshared)]

    # Function that updates the weights from the previously computed
    # gradient.
    f_update = theano.function([lr], [], updates=pup,
                               name='sgd_f_update')

    return f_grad_shared, f_update


def adadelta(lr, tparams, grads, x, xr, mask, y, cost):
    """
    An adaptive learning rate optimizer

    Parameters
    ----------
    lr : Theano SharedVariable
        Initial learning rate
    tpramas: Theano SharedVariable
        Model parameters
    grads: Theano variable
        Gradients of cost w.r.t to parameres
    x: Theano variable
        Model inputs
    mask: Theano variable
        Sequence mask
    y: Theano variable
        Targets
    cost: Theano variable
        Objective fucntion to minimize

    Notes
    -----
    For more information, see [ADADELTA]_.

    .. [ADADELTA] Matthew D. Zeiler, *ADADELTA: An Adaptive Learning
       Rate Method*, arXiv:1212.5701.
    """

    zipped_grads = [theano.shared(p.get_value() * numpy_floatX(0.),
                                  name='%s_grad' % k)
                    for k, p in tparams.items()]

    running_up2 = [theano.shared(p.get_value() * numpy_floatX(0.),
                                 name='%s_rup2' % k)
                   for k, p in tparams.items()]

    running_grads2 = [theano.shared(p.get_value() * numpy_floatX(0.),
                                    name='%s_rgrad2' % k)
                      for k, p in tparams.items()]

    zgup = [(zg, g) for zg, g in zip(zipped_grads, grads)]

    rg2up = [(rg2, 0.95 * rg2 + 0.05 * (g ** 2))
             for rg2, g in zip(running_grads2, grads)]

    f_grad_shared = theano.function([x, xr, mask, y], cost, updates=zgup + rg2up,
                                    name='adadelta_f_grad_shared')

    updir = [-tensor.sqrt(ru2 + 1e-6) / tensor.sqrt(rg2 + 1e-6) * zg
             for zg, ru2, rg2 in zip(zipped_grads,
                                     running_up2,
                                     running_grads2)]

    ru2up = [(ru2, 0.95 * ru2 + 0.05 * (ud ** 2))
             for ru2, ud in zip(running_up2, updir)]

    param_up = [(p, p + ud) for p, ud in zip(tparams.values(), updir)]
    f_update = theano.function([lr], [], updates=ru2up + param_up,
                               on_unused_input='ignore',
                               name='adadelta_f_update')
    return f_grad_shared, f_update


def rmsprop(lr, tparams, grads, x, mask, y, cost):
    """
    A variant of  SGD that scales the step size by running average of the
    recent step norms.

    Parameters
    ----------
    lr : Theano SharedVariable
        Initial learning rate
    tpramas: Theano SharedVariable
        Model parameters
    grads: Theano variable
        Gradients of cost w.r.t to parameres
    x: Theano variable
        Model inputs
    mask: Theano variable
        Sequence mask
    y: Theano variable
        Targets
    cost: Theano variable
        Objective fucntion to minimize

    Notes
    -----
    For more information, see [Hint2014]_.

    .. [Hint2014] Geoff Hinton, *Neural Networks for Machine Learning*,
       lecture 6a,
       http://cs.toronto.edu/~tijmen/csc321/slides/lecture_slides_lec6.pdf
    """

    zipped_grads = [theano.shared(p.get_value() * numpy_floatX(0.),
                                  name='%s_grad' % k)
                    for k, p in tparams.items()]
    running_grads = [theano.shared(p.get_value() * numpy_floatX(0.),
                                   name='%s_rgrad' % k)
                     for k, p in tparams.items()]
    running_grads2 = [theano.shared(p.get_value() * numpy_floatX(0.),
                                    name='%s_rgrad2' % k)
                      for k, p in tparams.items()]

    zgup = [(zg, g) for zg, g in zip(zipped_grads, grads)]
    rgup = [(rg, 0.95 * rg + 0.05 * g) for rg, g in zip(running_grads, grads)]
    rg2up = [(rg2, 0.95 * rg2 + 0.05 * (g ** 2))
             for rg2, g in zip(running_grads2, grads)]

    f_grad_shared = theano.function([x, mask, y], cost,
                                    updates=zgup + rgup + rg2up,
                                    name='rmsprop_f_grad_shared')

    updir = [theano.shared(p.get_value() * numpy_floatX(0.),
                           name='%s_updir' % k)
             for k, p in tparams.items()]
    updir_new = [(ud, 0.9 * ud - 1e-4 * zg / tensor.sqrt(rg2 - rg ** 2 + 1e-4))
                 for ud, zg, rg, rg2 in zip(updir, zipped_grads, running_grads,
                                            running_grads2)]
    param_up = [(p, p + udn[1])
                for p, udn in zip(tparams.values(), updir_new)]
    f_update = theano.function([lr], [], updates=updir_new + param_up,
                               on_unused_input='ignore',
                               name='rmsprop_f_update')

    return f_grad_shared, f_update


def concatenate(tensor_list, axis=0):
    """
    Alternative implementation of `theano.tensor.concatenate`.
    This function does exactly the same thing, but contrary to Theano's own
    implementation, the gradient is implemented on the GPU.
    Backpropagating through `theano.tensor.concatenate` yields slowdowns
    because the inverse operation (splitting) needs to be done on the CPU.
    This implementation does not have that problem.
    :usage:
        >>> x, y = theano.tensor.matrices('x', 'y')
        >>> c = concatenate([x, y], axis=1)
    :parameters:
        - tensor_list : list
            list of Theano tensor expressions that should be concatenated.
        - axis : int
            the tensors will be joined along this axis.
    :returns:
        - out : tensor
            the concatenated tensor expression.
    """
    concat_size = sum(tt.shape[axis] for tt in tensor_list)

    output_shape = ()
    for k in range(axis):
        output_shape += (tensor_list[0].shape[k],)
    output_shape += (concat_size,)
    for k in range(axis + 1, tensor_list[0].ndim):
        output_shape += (tensor_list[0].shape[k],)

    out = tensor.zeros(output_shape)
    offset = 0
    for tt in tensor_list:
        indices = ()
        for k in range(axis):
            indices += (slice(None),)
        indices += (slice(offset, offset + tt.shape[axis]),)
        for k in range(axis + 1, tensor_list[0].ndim):
            indices += (slice(None),)

        out = tensor.set_subtensor(out[indices], tt)
        offset += tt.shape[axis]

    return out


def param_init_fflayer(options, params, prefix='ff', nin=None, nout=None,
                       ortho=True):
    if nin is None:
        nin = options['dim']
    if nout is None:
        nout = options['dim']
    params[_p(prefix, 'W')] = norm_weight(nin, nout, scale=0.1, ortho=ortho)
    params[_p(prefix, 'b')] = numpy.zeros((nout,)).astype('float64')
    return params


def fflayer(tparams, state_below, options, prefix='conv',
            activ='lambda x: tensor.tanh(x)', **kwargs):
    return eval(activ)(
        tensor.dot(state_below, tparams[_p(prefix, 'W')]) + tparams[_p(prefix, 'b')])


def param_init_cnn(options, params, prefix='cnn', nin=None, dim=None):
    if nin is None:
        nin = options['dim_word']
    if dim is None:
        dim = options['dim']
    W = norm_weight(nin, dim, win=options['win'])
    print W.shape
    params[_p(prefix, 'W')] = W
    return params


def cnn_layer(tparams, state_below, options, prefix='cnn',
              mask=None, init_state=None, **kwargs):
    win = options['win']
    nsteps = state_below.shape[0] - win + 1

    print state_below.ndim

    if state_below.ndim == 3:  # state_below size [n_steps,n_samples,dim_word]
        n_samples = state_below.shape[1]
        dim_word = state_below.shape[2]
    else:  # state_below size [n_steps,dim_word]
        n_samples = 1
        dim_word = state_below.shape[1]

    dim = tparams[_p(prefix, 'W')].shape[2]  # W size [win,nin,dim]  filter num

    if mask is None:
        mask = tensor.alloc(1., nsteps, 1)

    # use scan to achieve CNN for n-gram
    # step function to be used by scan
    # arguments    | sequences |outputs-info| non-seqs
    def _step(m_, x_, xx_, xxx_, W):
        # preact = tensor.dot(h_, U)#recurrent input U*h_
        # preact+=x_+xx_+xxx_
        preact_x = tensor.dot(x_, W[0])
        preact_xx = tensor.dot(xx_, W[1])
        preact_xxx = tensor.dot(xxx_, W[2])
        #        preact_xxxx = tensor.dot(xxxx_, W[3])
        #        preact_xxxxx = tensor.dot(xxxxx_, W[4])
        preact = preact_x + preact_xx + preact_xxx
        h = tensor.nnet.relu(preact)
        h = m_[:, None] * h
        return h

    print "ccc"

    # prepare scan arguments
    shared_vars = [tparams[_p(prefix, 'W')]]
    print "ddd"
    # set initial state to all zeros
    if init_state is None:
        init_state = tensor.unbroadcast(tensor.alloc(0., n_samples, dim), 0)
    print "eee"
    rval, updates = theano.scan(_step,
                                sequences=[mask, dict(input=state_below, taps=[0, 1, 2])],  # here win=3
                                non_sequences=shared_vars,
                                name=_p(prefix, '_layers'),
                                n_steps=nsteps,
                                profile=profile,
                                strict=True)
    rval = [rval]
    return rval


def param_init_lstm(options, params, prefix='lstm'):
    """
    Init the LSTM parameter:

    :see: init_params
    """
    W = numpy.concatenate([ortho_weight(options['dim']),
                           ortho_weight(options['dim']),
                           ortho_weight(options['dim']),
                           ortho_weight(options['dim'])], axis=1)
    params[_p(prefix, 'W')] = W  # params["lstm_W"] = W

    U = numpy.concatenate([ortho_weight(options['dim']),
                           ortho_weight(options['dim']),
                           ortho_weight(options['dim']),
                           ortho_weight(options['dim'])], axis=1)
    params[_p(prefix, 'U')] = U  # params["lstm_U"] = U

    b = numpy.zeros((4 * options['dim'],))  # 1 * (4*128)
    params[_p(prefix, 'b')] = b.astype(config.floatX)  # params["lstm_b"] = b
    return params


def lstm_layer(tparams, state_below, options, prefix='lstm', mask=None):
    # state_below : [n_Step, BatchSize, Emb_Dim]
    nsteps = state_below.shape[0]  # n_Step 一句话的最长长度大小
    if state_below.ndim == 3:
        n_samples = state_below.shape[1]
    else:
        n_samples = 1

    assert mask is not None

    def _slice(_x, n, dim):
        if _x.ndim == 3:
            return _x[:, :, n * dim:(n + 1) * dim]
        return _x[:, n * dim:(n + 1) * dim]  # 运行该句 _x: BatchSize*4emb_dim

    # m_: mask(1D:BatchSize) , x_: 输入数据, h_:cell's output,  c_:the memory cells’ state at time t-1
    # h_, c_ : (BatchSize*emb_dim)
    # 按照sequences，outputs_info对_step里的参数赋值
    # _step这个函数有4个参数(m_, x_, h_, c_) 这里对应sequences的[mask, state_below]再加上outputs_info的两个，
    # _step输出是h,c,输出到outputs里，把一开始output_infos的两个zeros替换掉，进入下一轮
    # dot:矩阵乘法， *: 点乘
    def _step(m_, x_, h_, c_):
        preact = tensor.dot(h_, tparams[
            _p(prefix, 'U')])  # (BatchSize*dim_proj) * (emb_dim*4emb_dim) =  batchsize * 4emb_dim
        preact += x_

        # i,f,o,c: batchsize * emb_dim 
        i = tensor.nnet.sigmoid(_slice(preact, 0, options['dim']))
        f = tensor.nnet.sigmoid(_slice(preact, 1, options['dim']))
        o = tensor.nnet.sigmoid(_slice(preact, 2, options['dim']))
        c = tensor.tanh(_slice(preact, 3, options['dim']))

        c = f * c_ + i * c  # batchsize * emb_dim

        c = m_[:, None] * c + (1. - m_)[:, None] * c_

        h = o * tensor.tanh(c)
        h = m_[:, None] * h + (1. - m_)[:, None] * h_

        return h, c

    # (n_step*batchsize*emb_dim) * (emb_dim*4emb_dim) = (n_step * batchsize * 4emb_dim)
    state_below = (tensor.dot(state_below, tparams[_p(prefix, 'W')]) + tparams[_p(prefix, 'b')])
    # print(state_below.ndim) # 3
    # print(mask.ndim) # 2
    dim = options['dim']  # 128
    # tensor.alloc: 创建BatchSize*emb_dim大小的数值为0的数组
    # scan相当于是个loop，nsteps可以看作循环次数
    rval, updates = theano.scan(_step,
                                sequences=[mask, state_below],
                                outputs_info=[tensor.alloc(numpy_floatX(0.), n_samples, dim),
                                              tensor.alloc(numpy_floatX(0.), n_samples, dim)],
                                name=_p(prefix, '_layers'),
                                n_steps=nsteps)

    return rval[0]  # 即_step放回的h矩阵 3D:([n_Step, BatchSize, Emb_Dim])


# GRU layer
def param_init_gru(options, params, prefix='gru', nin=None, dim=None):
    if nin is None:
        nin = options['dim']
    if dim is None:
        dim = options['dim']

    # embedding to gates transformation weights, biases
    # W_r and W_z
    W = numpy.concatenate([norm_weight(nin, dim),
                           norm_weight(nin, dim)], axis=1)
    # params["encoder_W"] = W[ (512*1024) , (512*1024) ]
    params[_p(prefix, 'W')] = W
    # params["encoder_b"] = b[ (2048*1) ]
    params[_p(prefix, 'b')] = numpy.zeros((2 * dim,)).astype(config.floatX)

    # recurrent transformation weights for gates
    # U_r and U_z
    U = numpy.concatenate([ortho_weight(dim),
                           ortho_weight(dim)], axis=1)
    # params["encoder_U"] = U[ (1024*1024) , (1024*1024) ]
    params[_p(prefix, 'U')] = U

    # hidden state
    # embedding to hidden state proposal weights, biases
    Wx = norm_weight(nin, dim)
    # params["encoder_Wx"] = Wx[ (512*1024) ]
    params[_p(prefix, 'Wx')] = Wx

    # params["encoder_bx"] = bx[ (1024*1) ]
    params[_p(prefix, 'bx')] = numpy.zeros((dim,)).astype(config.floatX)

    # recurrent transformation weights for hidden state proposal
    Ux = ortho_weight(dim)
    # params["encoder_Ux"] = Ux[ (1024*1024) ]
    params[_p(prefix, 'Ux')] = Ux

    return params


def gru_layer(tparams, state_below, options, prefix='gru', mask=None,
              **kwargs):
    # state_below : [n_timesteps, n_samples, dim_word]
    nsteps = state_below.shape[0]  # n_timesteps: a sentence max len
    if state_below.ndim == 3:
        n_samples = state_below.shape[1]
    else:
        n_samples = 1

    dim = tparams[_p(prefix, 'Ux')].shape[1]  # 1024 is gru number of hidden units.

    if mask is None:
        mask = tensor.alloc(1., state_below.shape[0], 1)  # dtype=float32, n_timesteps*1: a matrix, it's value is 1

    # utility function to slice a tensor
    def _slice(_x, n, dim):
        if _x.ndim == 3:
            return _x[:, :, n * dim:(n + 1) * dim]
        return _x[:, n * dim:(n + 1) * dim]  # run it, BatchSize*2emb_dim

    # state_below is the input word embeddings
    # input to the gates, concatenated
    # (n_timesteps*n_samples*dim_word) * (dim_word*2dim) = (n_timesteps * n_samples * 2dim)
    state_below_ = tensor.dot(state_below, tparams[_p(prefix, 'W')]) + tparams[_p(prefix, 'b')]
    # input to compute the hidden state proposal
    state_belowx = tensor.dot(state_below, tparams[_p(prefix, 'Wx')]) + tparams[_p(prefix, 'bx')]

    # step function to be used by scan
    # arguments    | sequences |outputs-info| non-seqs
    def _step_slice(m_, x_, xx_, h_, U, Ux):
        preact = tensor.dot(h_, U)
        preact += x_
        # reset and update gates
        r = tensor.nnet.sigmoid(_slice(preact, 0, dim))
        u = tensor.nnet.sigmoid(_slice(preact, 1, dim))

        # compute the hidden state proposal
        preactx = tensor.dot(h_, Ux)
        preactx = preactx * r
        preactx = preactx + xx_

        # hidden state proposal
        h = tensor.tanh(preactx)

        # leaky integrate and obtain next hidden state
        h = u * h_ + (1. - u) * h
        h = m_[:, None] * h + (1. - m_)[:, None] * h_

        return h

    # prepare scan arguments
    seqs = [mask, state_below_, state_belowx]
    init_states = [tensor.alloc(numpy_floatX(0.), n_samples, dim)]  # n_samples * dim
    _step = _step_slice
    shared_vars = [tparams[_p(prefix, 'U')],
                   tparams[_p(prefix, 'Ux')]]

    rval, updates = theano.scan(_step,
                                sequences=seqs,
                                outputs_info=init_states,
                                non_sequences=shared_vars,
                                name=_p(prefix, '_layers'),
                                n_steps=nsteps,
                                profile=profile,
                                strict=True)
    rval = [rval]
    return rval


def init_params(options, wemb):
    """
    Global (not LSTM) parameter. For the embeding and the classifier.
    """
    params = OrderedDict()  # 实现了对字典对象中元素的排序
    # embedding
    randn = wemb
    # print wemb.shape
    # astype(type): returns a copy of the array converted to the specified type.
    # 'Wemb' : word embedding 词向量空间数组
    params['Wemb'] = randn.astype(config.floatX)

    params = get_layer(options['decoder'])[0](options, params,
                                              prefix='decoder',
                                              nin=options['dim_word'],
                                              dim=options['dim'])

    params = get_layer(options['decoder'])[0](options, params,
                                              prefix='decoder_r',
                                              nin=options['dim_word'],
                                              dim=options['dim'])

    # classifier 初始化Softmax输出层参数  U：128*2   b:1*2
    params['U'] = 0.01 * numpy.random.randn(2 * options['dim'], options['ydim']).astype(config.floatX)
    # print params['U'].shape
    params['b'] = numpy.zeros((options['ydim'],)).astype(config.floatX)
    # print params['b'].shape


    return params


def build_model(tparams, options):
    trng = RandomStreams(1234)
    use_noise = theano.shared(numpy.float64(0.))

    x = tensor.matrix('x', dtype='int64')
    xr = tensor.matrix('xr', dtype='int64')
    x_mask = tensor.matrix('x_mask', dtype='float64')
    # x_target=tensor.matrix('x_target', dtype='int64')
    y = tensor.vector('y', dtype='int64')
    n_timesteps = x.shape[0]
    n_samples = x.shape[1]

    # input
    emb = tparams['Wemb'][x.flatten()]
    emb = emb.reshape([n_timesteps, n_samples, options['dim_word']])

    proj = get_layer(options['decoder'])[1](tparams, emb, options,
                                            prefix='decoder',
                                            mask=x_mask)

    embr = tparams['Wemb'][xr.flatten()]
    embr = embr.reshape([n_timesteps, n_samples, options['dim_word']])

    projr = get_layer(options['decoder'])[1](tparams, embr, options,
                                             prefix='decoder_r',
                                             mask=x_mask)
    ctx = concatenate([proj[0], projr[0]], axis=proj[0].ndim - 1)

    proj = (ctx * x_mask[:, :, None]).sum(axis=0)
    proj = proj / x_mask.sum(axis=0)[:, None]

    if options['use_dropout']:
        proj = dropout_layer(proj, use_noise, trng)

    pred = tensor.nnet.softmax(tensor.dot(proj, tparams['U']) + tparams['b'])
    f_pred_prob = theano.function([x, xr, x_mask], pred, name='f_pred_prob')  # 预测的每个类的概率
    f_pred = theano.function([x, xr, x_mask], pred.argmax(axis=1), name='f_pred')  # 预测出的类别
    off = 1e-8
    if pred.dtype == 'float16':
        off = 1e-6
    cost_logit = -tensor.log(pred[tensor.arange(n_samples), y] + off).mean()  # cost function

    cost = cost_logit

    return use_noise, x, xr, x_mask, y, f_pred_prob, f_pred, cost


# 用于预测一些新的example，输出预测结果为[n_sample,y_dim]的矩阵
def pred_probs(f_pred_prob, prepare_data, data, iterator, verbose=False):
    """ If you want to use a trained model, this is useful to compute
    the probabilities of new examples.
    """
    n_samples = len(data[0])
    probs = numpy.zeros((n_samples, 2)).astype(config.floatX)

    n_done = 0

    for _, valid_index in iterator:
        x, xr, mask, y = prepare_data([data[0][t] for t in valid_index],
                                      numpy.array(data[1])[valid_index],
                                      maxlen=None)
        pred_probs = f_pred_prob(x, xr, mask)
        probs[valid_index, :] = pred_probs

        n_done += len(valid_index)
        if verbose:
            print('%d/%d samples classified' % (n_done, n_samples))

    return probs


# 计算误差，传入函数的地址作为参数，f_pred（预测的函数,输出结果为一个n_sample的向量, prepare_data ： 补零，加mask
def pred_error(f_pred, prepare_data, data, iterator, verbose=False):
    """
    Just compute the error
    f_pred: Theano fct computing the prediction
    prepare_data: usual prepare_data for that dataset.
    """
    valid_err = 0
    for _, valid_index in iterator:
        x, xr, mask, y = prepare_data([data[0][t] for t in valid_index],
                                      numpy.array(data[1])[valid_index],
                                      maxlen=None)
        preds = f_pred(x, xr, mask)
        targets = numpy.array(data[1])[valid_index]
        valid_err += (preds == targets).sum()
    valid_err = 1. - numpy_floatX(valid_err) / len(data[0])

    return valid_err


def train(dim_word=100,  # word vector dimensionality
          dim=1000,  # the number of GRU units
          encoder='cnn',
          decoder='lstm',
          decoder_cond='lstm',
          win=5,
          patience=100,  # early stopping patience
          max_epochs=50,
          finish_after=10000000,  # finish after this many updates
          dispFreq=20,
          decay_c=0.,  # L2 weight decay penalty
          lrate=0.01,
          n_words=100000,  # vocabulary size
          maxlen=100,  # maximum length of the description
          optimizer=adadelta,
          batch_size=16,
          test_size=300,
          valid_batch_size=16,
          saveto='model.npz',
          validFreq=1000,
          saveFreq=1000,  # save the parameters after every saveFreq updates
          sampleFreq=100,  # generate some samples after every sampleFreq
          use_dropout=False,
          overwrite=False,
          reload_=False):
    # Model options
    model_options = locals().copy()

    print model_options

    print "loading data...",
    x = cPickle.load(open("mr_company_new.p", "rb"))
    revs, W, W2, word_idx_map, vocab = x[0], x[1], x[2], x[3], x[4]
    print "data loaded!"
    mode = "-nonstatic"
    word_vectors = "-word2vec"
    if mode == "-nonstatic":
        print "model architecture: CNN-non-static"
        non_static = True
    elif mode == "-static":
        print "model architecture: CNN-static"
        non_static = False
    # execfile("conv_net_classes.py")    
    if word_vectors == "-rand":
        print "using: random vectors"
        U = W2
    elif word_vectors == "-word2vec":
        print "using: word2vec vectors"
        U = W
    results = []
    print U.shape
    print len(revs)

    train, valid, test = load_data(revs, word_idx_map, n_words=n_words, valid_portion=0.1, maxlen=maxlen)
    if test_size > 0:
        # The test set is sorted by size, but we want to keep random
        # size example.  So we must select a random selection of the
        # examples.
        idx = numpy.arange(len(test[0]))
        numpy.random.shuffle(idx)
        idx = idx[:test_size]
        test = ([test[0][n] for n in idx], [test[1][n] for n in idx])
    print len(train[0])
    print len(valid[0])
    print len(test[0])

    ydim = 2

    model_options['ydim'] = ydim

    print('Building model')
    # This create the initial parameters as numpy ndarrays.
    # Dict name (string) -> numpy ndarray
    params = init_params(model_options, U)

    print "aaa"

    # reload parameters
    if reload_ and os.path.exists(saveto):
        params = load_params(saveto, params)

    # create shared variables for parameters
    tparams = init_tparams(params)
    print tparams.values()
    print list(tparams.values())
    print "bbb"

    # build the symbolic computational graph
    (use_noise, x, xr, mask, y, f_pred_prob, f_pred, cost) = build_model(tparams, model_options)

    if decay_c > 0.:
        decay_c = theano.shared(numpy_floatX(decay_c), name='decay_c')
        weight_decay = 0.
        for kk, vv in tparams.iteritems():
            weight_decay += (vv ** 2).sum()
        weight_decay *= decay_c
        cost += weight_decay
    # inps = [x, x_target,x_mask]

    f_cost = theano.function([x, xr, mask, y], cost, name='f_cost')  # 求cost function 这句没用到
    print "mmm"

    grads = tensor.grad(cost, wrt=list(tparams.values()))
    print "nnn"
    f_grad = theano.function([x, xr, mask, y], grads, name='f_grad')  # 求cost function对每个参数的梯度
    print "ooo"
    lr = tensor.scalar(name='lr')
    print "ppp"
    # f_grad_shared：把每个参数的梯度封装成shared变量??? f_update： 梯度更新????
    f_grad_shared, f_update = optimizer(lr, tparams, grads, x, xr, mask, y, cost)
    print "qqq"

    print('Optimization')

    kf_valid = get_minibatches_idx(len(valid[0]), valid_batch_size)  # 返回验证集的批量次数和批量数据
    kf_test = get_minibatches_idx(len(test[0]), valid_batch_size)

    print("%d train examples" % len(train[0]))  # 7600
    print("%d valid examples" % len(valid[0]))  # 400
    print("%d test examples" % len(test[0]))  # 359

    history_errs = []
    best_p = None  # best params
    bad_count = 0

    #    if validFreq == -1:
    #        validFreq = len(train[0]) // batch_size
    #    if saveFreq == -1:
    #        saveFreq = len(train[0]) // batch_size

    uidx = 0  # the number of update done
    estop = False  # early stop
    start_time = time.time()
    # eidx：迭代索引
    try:
        for eidx in range(max_epochs):
            n_samples = 0
            costs = []
            # Get new shuffled index for the training set.
            kf = get_minibatches_idx(len(train[0]), batch_size, shuffle=True)
            one_epoch_start = time.time()
            for _, train_index in kf:
                uidx += 1

                use_noise.set_value(1.)
                # Select the random examples for this minibatch
                x = [train[0][t] for t in train_index]
                y = [train[1][t] for t in train_index]
                # Get the data in numpy.ndarray format
                # This swap the axis!
                # Return something of shape (minibatch maxlen, n samples)
                x, xr, mask, y = prepare_data(x, y)
                n_samples += x.shape[1]
                cost = f_grad_shared(x, xr, mask, y)
                costs.append(cost)
                # print "rrr"
                f_update(lrate)  # # Learning rate for sgd (not used for adadelta and rmsprop)

                if numpy.isnan(cost) or numpy.isinf(cost):
                    print('bad cost detected: ', cost)
                    return 1., 1., 1.
                # 显示更新进度，10次mini_batch后
                if dispFreq > 0 and numpy.mod(uidx, dispFreq) == 0:
                    print('Epoch ', eidx, 'Update ', uidx, 'Cost ', cost)

                if saveFreq > 0 and saveto and numpy.mod(uidx, saveFreq) == 0:
                    print('Saving...')

                    if best_p is not None:
                        params = best_p
                    else:
                        params = unzip(tparams)
                    numpy.savez(saveto, history_errs=history_errs, **params)
                    pickle.dump(model_options, open('%s.pkl' % saveto, 'wb'), -1)
                    print('Done')

                if validFreq > 0 and numpy.mod(uidx, validFreq) == 0:
                    use_noise.set_value(0.)
                    train_err = pred_error(f_pred, prepare_data, train, kf)
                    valid_err = pred_error(f_pred, prepare_data, valid, kf_valid)
                    test_err = pred_error(f_pred, prepare_data, test, kf_test)

                    history_errs.append([valid_err, test_err])

                    if (best_p is None or valid_err <= numpy.array(history_errs)[:, 0].min()):
                        best_p = unzip(tparams)
                        bad_counter = 0

                    print(('Train perf', 1 - train_err, 'Valid perf', 1 - valid_err, 'Test perf', 1 - test_err))

                    if (len(history_errs) > patience and valid_err >= numpy.array(history_errs)[:-patience, 0].min()):
                        bad_counter += 1
                        if bad_counter > patience:
                            print('Early Stop!')
                            estop = True
                            break
            if saveFreq == -1:
                print('Saving...')

                if best_p is not None:
                    params = best_p
                else:
                    params = unzip(tparams)
                numpy.savez(saveto, history_errs=history_errs, **params)
                pickle.dump(model_options, open('%s.pkl' % saveto, 'wb'), -1)
                print('Done')

            if validFreq == -1:
                use_noise.set_value(0.)
                train_err = pred_error(f_pred, prepare_data, train, kf)
                valid_err = pred_error(f_pred, prepare_data, valid, kf_valid)
                test_err = pred_error(f_pred, prepare_data, test, kf_test)

                history_errs.append([valid_err, test_err])

                if (best_p is None or valid_err <= numpy.array(history_errs)[:, 0].min()):
                    best_p = unzip(tparams)
                    bad_counter = 0

                print(('Train perf', 1 - train_err, 'Valid perf', 1 - valid_err, 'Test perf', 1 - test_err))

                if (len(history_errs) > patience and valid_err >= numpy.array(history_errs)[:-patience, 0].min()):
                    bad_counter += 1
                    if bad_counter > patience:
                        print('Early Stop!')
                        estop = True
                        break

            one_epoch_time = time.time() - one_epoch_start
            print('Epoch ', eidx, 'Update ', uidx, 'Cost ', numpy.mean(costs), 'one_epoch_time ', one_epoch_time)
            print('Seen %d samples' % n_samples)

            if estop:
                break

    except KeyboardInterrupt:
        print("Training interupted")

    end_time = time.time()
    if best_p is not None:
        zipp(best_p, tparams)
    else:
        best_p = unzip(tparams)

    use_noise.set_value(0.)
    kf_train_sorted = get_minibatches_idx(len(train[0]), batch_size)
    train_err = pred_error(f_pred, prepare_data, train, kf_train_sorted)
    valid_err = pred_error(f_pred, prepare_data, valid, kf_valid)
    test_err = pred_error(f_pred, prepare_data, test, kf_test)

    print('Train perf: ', 1 - train_err, 'Valid perf: ', 1 - valid_err, 'Test perf: ', 1 - test_err)
    if saveto:
        numpy.savez(saveto, train_err=train_err,
                    valid_err=valid_err, test_err=test_err,
                    history_errs=history_errs, **best_p)
    print('The code run for %d epochs, with %f sec/epochs' % (
        (eidx + 1), (end_time - start_time) / (1. * (eidx + 1))))

    # print( ('Training took %.1fs' % (end_time - start_time)), file=sys.stderr)

    return train_err, valid_err, test_err
