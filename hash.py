import base64
from turtle import pos
from bitstring import BitArray
import random
from math import ceil, log2
import io

def calcular_entropia(data):
    char_ = []
    for chars in data:
        if chars not in char_:
            char_.append(chars)

    entropy = len(data)*log2(len(char_))

    return data, entropy

def return_base64(word_bin):
    return base64.b64encode(word_bin)

def to_bin(word):
    word_bin = BitArray(bytes=word)
    return word_bin

def operations(word_bin, n_cut = 1):
    new_bit_array = BitArray()
    for segmentos in word_bin.cut(n_cut):
        i = 0

        while i + n_cut <= word_bin.len:
            segmentos = segmentos^word_bin[i:i+n_cut]
            i = i + n_cut

        # Se definen semillas
        seed_0 = segmentos.count(1)
        seed_1 = segmentos.count(0)

        random.seed(seed_0*seed_1)
        random_seed = random.randint(1,20)

        segmentos.ror(random_seed)
        segmentos.invert()

        new_bit_array.append(segmentos)
    
    random.seed(word_bin.count(1))
    random_seed = random.randint(1,word_bin.len-1)

    new_bit_array.rol(random_seed)

    return new_bit_array

def hash(word_bin):
    largo = word_bin.len

    # Se creará un hash de 60 caracteres en base64 -> 480 bits
    if largo%480 != 0:
        word_bin = padding(word_bin, largo)

    word_seg = BitArray(length=480, offset=0)
    for segmentos in word_bin.cut(480):
        # Se definen semillas
        seed_0 = segmentos.count(1)
        seed_1 = segmentos.count(0)

        seed_multiply = seed_0 * seed_1
        random.seed(seed_multiply)
        
        # Bytes aleatorios según la semilla
        random_bytes = random.randbytes(60)

        # Nuevo objeto BitArray
        new_array_b = BitArray(bytes=random_bytes)

        # XOR entre segmento y hash
        word_seg = word_seg ^ segmentos

        # XOR entre bytes aleatorios y hash
        word_seg = word_seg ^ new_array_b

        # Rotación hacia la derecha utilizando la misma semilla para cantidad de rotaciones
        n_rot = random.randint(1, 7)
        word_seg.ror(n_rot)
    
    return operations(word_seg, 20)
    
def padding(word_bin, largo):
    paridad = word_bin.count(1)
    seed_0 = paridad
    seed_1 = largo

    # Cantidad de bits a agregar
    n_bits = 480 - largo%480
    n_bytes = ceil(n_bits/8)

    # Se crean bytes aleatorios con n_bytes como cantidad
    # Se utilizan semillas conocidas: paridad y largo
    # Seed 0
    random.seed(seed_0)
    random_seed_0 = random.randbytes(n_bytes)
    # Seed 1
    random.seed(seed_1)
    random_seed_1 = random.randbytes(n_bytes)

    # Bytes random se convierten a un objeto BitArray
    pad_0 = BitArray(bytes=random_seed_0)
    pad_1 = BitArray(bytes=random_seed_1)

    # Se hace XOR entre ambos objetos
    pad_final = pad_0^pad_1

    # Se define una rotación aleatoria con la cantidad de 0 como semilla
    seed_rot = word_bin.count(0)
    random.seed(seed_rot)
    n_rot = random.randint(1,7)

    # Rotación izquierda
    pad_final.rol(n_rot)

    # Se invierten los bits
    pad_final = ~pad_final

    # Por último se cortan a la cantidad requerida
    if n_bytes*8!=n_bits: del pad_final[-(pad_final.len-n_bits):]
    
    word_bin.append(pad_final)

    return word_bin

def main(arg, std = False):

    if isinstance(arg, (bytes, bytearray)):
            arg = io.BytesIO(arg)
       
    if std:             
        arg = arg.readline()
        arg = arg[0:len(arg)-2]
    else:
         data = arg.read()
         arg = data
    
    #Byte -> BitArray
    input_ = BitArray(bytes=arg)
    
    # Hash
    res_hash= hash(input_)


    # Base 64
    res_hash_b64 = return_base64(res_hash.bytes)
    res = res_hash_b64.decode('ascii')

    print("Hash resultante:\n" + res)

if __name__ == '__main__':
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs='*',
                        help='input file or message to hash')
    args = parser.parse_args()

    data = None

    if len(args.input) == 0:
        print('(1) Calcular Hash de texto')
        print('(2) Calcular entropía de texto')

        option = -1
        while(option!=1 and option != 2):
            try:
                option = int(input('Ingrese el número de la opción: '))
                if(option!=1 and option != 2): print('Error: ingrese una opción válida')
            except ValueError:
                print('---------------------------------------')
                print('\n¡Error: ingrese una opción válida!\n')
                print('(1) Calcular Hash de texto')
                print('(2) Calcular entropía de texto')


        if option==1:
            sys.stdout.write("\nIngrese texto:\n")
            sys.stdout.flush()
            data = sys.stdin.detach()
            
            # Output to console
            main(data, std=True)
        elif option ==2:
            data = input('\nIngrese texto:\n')
            txt, entropy = calcular_entropia(data)
            sys.stdout.flush()
            sys.stdout.write("-------------------------------\n")
            sys.stdout.write("TEXTO:\n" + txt)
            sys.stdout.write('\nENTROPÍA:\n' + str(entropy))
            sys.stdout.write("\n-------------------------------")


    else:
        # Loop through arguments list
        print('(1) Calcular Hash de texto')
        print('(2) Calcular entropía de texto')
        option = int(input('Ingrese el número de la opción: '))

        while option!=1 and option!=2:
            print('Opción inválida')
            option = int(input('Ingrese el número de la opción: '))

        for argument in args.input:
            if (os.path.isfile(argument)):
                # An argument is given and it's a valid file. Read it
                data = open(argument, 'rb')                

                # Show the final digest
                if option == 1:
                    main(data)
                elif option == 2:
                    txt, entropy = calcular_entropia(data.read())
                    sys.stdout.flush()
                    sys.stdout.write("-------------------------------\n")
                    sys.stdout.write("TEXTO:\n" + txt.decode('utf-8'))
                    sys.stdout.write('\nENTROPÍA:\n' + str(entropy))
                    sys.stdout.write("\n-------------------------------")
            else:
                print("Error, could not find " + argument + " file." )
