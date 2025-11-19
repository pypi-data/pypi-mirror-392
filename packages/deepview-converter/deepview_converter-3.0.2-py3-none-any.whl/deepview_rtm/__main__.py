
import os,sys
import numpy as np
from argparse import ArgumentParser


def convert():
    parser = ArgumentParser(description="RTM Converter")
    parser.add_argument("infile", type=str, help="Filename of the model to be converted to RTM")
    parser.add_argument("outfile", type=str, help="Output filename for the RTM model")
    parser.add_argument("--samples", type=str, default='', help="The location of dataset samples to be used for quantization. " \
                        "This can be a filepath to a folder containing images or a URL to a datastore containing images.")
    parser.add_argument("--crop", action='store_true', help="When using datastore URL in the samples, " \
                        "then you need to set the crop flag in case of classification.")
    parser.add_argument("--quant_tensor", "--quant-tensor", action='store_true',
                        help="Flag to determine if we should change to per tensor quantization")
    parser.add_argument("--quant_channel", "--quant-channel", action='store_true',
                        help="Flag to determine if we should change to per channel quantization")
    parser.add_argument("--quantize", action='store_true',
                        help="Flag used to quantize Saved Model and Keras models")
    parser.add_argument("--input_type", "--input-type", type=str, default='none', choices=["none", "float32", "int8", "uint8"],
                        help="Model input data type")
    parser.add_argument("--output_type", "--output-type", type=str, default='none', choices=["none", "float32", "int8", "uint8"],
                        help="Model output data type")
    parser.add_argument("--onnx_input_format", "--onnx-input-format", type=str, default='none', 
                        choices=["none", "float32", "int8", "uint8"],
                        help="Input type of ONNX input model, used for quantization")
    parser.add_argument("--input_names", "--input-names", type=str, default='',
                        help="Input layers in the final converted model. Output model can be a subgraph depending on this field.")
    parser.add_argument("--output_names", "--output-names", type=str, default='',
                        help="Output layers in the final converted model. Output model can be a subgraph depending on this field.")
    parser.add_argument("--use_svm", "--use-svm", type=str, default='',
                        help="SVM filepath")
    parser.add_argument("--constant", type=str, default='',
                        help="Comma delimited list of constants to add to model; const_name1=array1.npy,const_name2=array2.npy...")
    parser.add_argument("--input_shape", "--input-shape", "--default_shape", "--default-shape", type=str,
                        default="1,224,224,3", help="Comma delimited input shape")
    parser.add_argument("--save_map", "--save-map", type=str, default='', help="Filename of where to save the memory map allocation")
    parser.add_argument("--no_map", "--no-map", action='store_true',
                        help="Flag to disable memory mapping")
    parser.add_argument("--save_layers", "--save-layers", type=str, default='',
                        help="Comma delimited list of layers to not be overwritten in the memory map")
    parser.add_argument("--copy_layers", "--copy-layers", type=str, default='',
                        help="List of layers and their target layer to which they will be copied at the end of each inference")
    parser.add_argument("--labels", type=str, default='', help="Filename of where the labels are stored or a " \
                        "comma-delimited list of labels")
    parser.add_argument("--skip_optimizations", "--skip-optimizations", type=str, 
                        default="conv_mul4,concatN,sigmoid_expand,quantize_dequant_ops")
    parser.add_argument("--panel_shuffle", "--panel-shuffle", type=str,
                        default='none', choices=['none', 'armv7', 'armv8', 'sse', 'avx2'])
    parser.add_argument("--user_ops", "--user-ops", type=str, default='',
                        help="Additional user op handlers for custom layers")
    parser.add_argument("--quant_normalization", "--quant-normalization", "--normalization", type=str,
                        default='none', choices=["none", "whitening", "signed", "unsigned"],
                        help="The normalization method to use for quantization")
    parser.add_argument("--force_quant_tensor", "--force-quant-tensor",
                        action='store_true', help="Force the conversion to override partial quantization and use full quantization")
    parser.add_argument("--activation_datatype", "--activation-datatype", type=str, default='none',
                        choices=['none', 'float32', 'int8', 'uint8'])
    parser.add_argument("--transpose_conv_filter_datatype", "--transpose-conv-filter-datatype", type=str,
                        default='none', choices=['none', 'float32', 'int8', 'uint8'])
    parser.add_argument("--model_input_type", "--model-input-type", type=str, default='none',
                        choices=["none", "float32", "int8", "uint8"])
    parser.add_argument("--nnef_format", "--nnef-format", type=str, default="nchw", choices=['nhwc', 'nchw'])
    parser.add_argument("--num_samples", "--num-samples", type=int, default=10,
                        help="Number of samples to use for quantization")
    parser.add_argument("--name", type=str, default='', help="Name of the model to store in metadata")
    parser.add_argument("--optimize_map", "--optimize-map", action='store_false',
                        help="Flag to disable memory map optimization")
    parser.add_argument("--metadata", action="append", help="Metadata to be stored within the model. " \
                        "Follows the format filename,metadata_field_name(optional),mime_type(optional)")
    args = parser.parse_args()

    src_type = args.infile.rsplit('.', 1)[-1]

    # try:
    tflite_ext = 'tflite'
    onnx_ext = 'onnx'

    samples = [args.samples, args.crop]

    if args.quant_tensor and args.quant_channel:
        raise ValueError(
            "Please use only one of --quant-tensor and --quant-channel")

    if (args.force_quant_tensor and not args.quant_tensor and args.quant_channel):
        raise ValueError(
            "--force-quant-tensor is only valid when converting to RTM and enable --quant-tensor.")

    if (args.quant_tensor or args.quant_channel) and not args.quantize:
        if src_type==tflite_ext or src_type == onnx_ext:
            print("WARNING: Ensure that the input model is quantized "
                "when using quant-tensor or quant-channel. Otherwise they "
                "will have no effect.")
        else:
            raise ValueError("Ensure that the input model is quantized "
                            "when using quant-tensor or quant-channel. For non-TFLite/ONNX "
                            "models, use --quantize.")

    if src_type == tflite_ext and args.quantize:
        raise ValueError("TFLite models cannot be quantized when "
                        "converting to an RTM model. Either use a pre-quantized "
                        "TFLite file or use an H5, Saved Model, or TFHub model when "
                        "using the argument --quantize.")

    if src_type == onnx_ext and args.quantize:
        raise ValueError("ONNX models cannot be quantized currently when "
                        "they are the source model.")

    try:
        onnx_input_format=args.onnx_input_format
    except:
        onnx_input_format='none'

    if onnx_input_format != 'none' and src_type == onnx_ext:
        raise ValueError("The argument --onnx_input_format is only for use when "
                        "converting from ONNX to RTM.")

    if args.input_names == '' or args.input_names is None:
        input_names = None
    else:
        input_names = args.input_names.split(',')

    if args.output_names == '' or args.output_names is None:
        output_names = None
    else:
        output_names = args.output_names.split(',')

    if args.model_input_type == 'int8':
        model_input_type = np.int8
    elif args.model_input_type == 'uint8':
        model_input_type = np.uint8
    else:
        model_input_type = np.float32

    args.input_shape = [int(x) for x in args.input_shape.split(',')]

    # ----------------------------  Optimizer   -----------------------------------

    
    if args.use_svm == '':
        svm = None
    else:
        svm = args.use_svm
        
    constant_dict = {}
    if args.constant!='':
        constant_list = args.constant.split(',') 
        for item in constant_list:
            val = item.split('=')
            filename =''
            name=val[0]
            if len(val) > 1: 
                filename=val[1]
            if os.path.isfile(filename):
                try:
                    print("Using Constant: " + filename)
                    sys.stdout.flush()
                    numpy_val = np.load(filename)
                except ValueError:
                    raise ValueError(
                        "Unable to load file: %s, ensure it is a numpy file." % filename)
            else:
                if not (args.infile.endswith('.pb') or args.infile.endswith('.onnx') or args.infile.endswith('.tflite')):
                    raise ValueError(
                        "Can only generate constants with ONNX, TF 1.x, and TFLite, please use a numpy file."+filename)
                # try:
                from deepview_rtm.utils import gen_constant
                numpy_val = gen_constant(
                    args.infile, args.input_shape, filename)
                # except Exception:
                #     raise ValueError("Unable to generate constant, ensure %s is a layer in the model "
                #                     "or use a numpy file.")
            if name == 'ssd_anchor_boxes':
                constant_dict[name] = numpy_val.reshape(-1,4).copy()
            else:
                constant_dict[name] = numpy_val

    if args.save_map == '':
        save_map = None
    else:
        save_map = args.save_map

    if args.no_map:
        mem_map = False
    else:
        mem_map = True

    if args.save_layers == '' or args.save_layers == []:
        save_layers = []
    else:
        save_layers = args.save_layers.split(',')

    if args.copy_layers == '' or args.copy_layers == []:
        copy_layers = []
    else:
        copy_layers = []
        copy_args = args.copy_layers.split(',')
        if len(copy_args) % 2 != 0:
            raise ValueError("There must be an even number of layers")
        for i in range(0, len(copy_args), 2):
            copy_layers.append((copy_args[i], copy_args[i + 1]))

    if args.labels == '' or args.labels == [] or args.labels == None:
        labels = None
    elif os.path.isfile(args.labels):
        with open(args.labels, 'r') as f:
            labels = f.read().split('\n')
    else:
        labels = array = [v for v in args.labels.split(',')]   
        if not len(labels) > 0:
            print("Could not find provided labels file")
            raise FileNotFoundError

    if args.skip_optimizations == '' or args.skip_optimizations==[]:
        skip_optimizations = []
    else:
        skip_optimizations = args.skip_optimizations

    if args.panel_shuffle == 'none':
        panel_shuffle = None
    else:
        panel_shuffle = args.panel_shuffle

    user_ops = []
    if args.user_ops =='' or args.user_ops==['']:
        args.user_ops =None

    if args.user_ops is not None:
        for user in args.user_ops:
            print('Loading custom user_ops handler %s' % user)
            sys.path.append(os.path.dirname(user))
            user_mod = os.path.splitext(os.path.basename(user))[0]
            user_ops.append(__import__(user_mod))

    subgraph_names = []
    if args.input_names or args.output_names:
        if args.input_names is None or args.input_names == '':
            subgraph_names.append([])
        else:
            subgraph_names.append(args.input_names.split(','))
        if args.output_names is None or args.output_names == '':
            subgraph_names.append([])
        else:
            subgraph_names.append(args.output_names.split(','))

    try:
        from deepview_rtm.optimizer import DeepViewOptimizer
        #imports import file in memory as a graph
        optimizer = DeepViewOptimizer(args.infile,
                                    args.nnef_format,
                                    skip_optimizations,
                                    panel_shuffle,
                                    args.input_shape,
                                    user_ops,
                                    args.quantize,
                                    args.input_type,
                                    args.output_type,
                                    samples,
                                    args.num_samples,
                                    model_input_type,
                                    subgraph_names,
                                    args.quant_tensor,
                                    args.quant_channel,
                                    args.force_quant_tensor,
                                    args.quant_normalization,
                                    args.activation_datatype,
                                    args.transpose_conv_filter_datatype,
                                    onnx_input_format)

    except ImportError as e:
        raise e
    except Exception as err:
        if int(os.getenv("DEEPVIEW_CONVERTER_DEBUG", 0)) > 0:
            raise err
        else:
            print("Unable to initialize the optimizer, set DEEPVIEW_CONVERTER_DEBUG=1 for traceback")
            sys.exit(0)


    try:

        from deepview_rtm.exporter_v1 import DeepViewExporter
        exporter = DeepViewExporter(optimizer, name=args.name, mem_map=mem_map,
                                    opt_map=args.optimize_map, save_map=save_map,
                                    save_layers=save_layers, copy_layers=copy_layers,
                                    svm=svm, ext_constants=constant_dict,
                                    labels=labels,
                                    input_names=input_names, output_names=output_names,
                                    user_ops=user_ops,
                                    normalization=args.quant_normalization,
                                    metadata=args.metadata)                                        
        buffer = exporter.run()
    
    except ImportError as e:
        raise e
    except Exception as err:
        if int(os.getenv("DEEPVIEW_CONVERTER_DEBUG", 0)) > 0:
            raise err
        else:
            print("Unable to convert the model, set DEEPVIEW_CONVERTER_DEBUG=1 for traceback")
            sys.exit(0)

    print("Saving File")

    with open(args.outfile, 'wb') as f:
        f.write(buffer)
    
if __name__ == '__main__':
    convert()
