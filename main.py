import cv2

def Embed(img, message):
    # Turn message into array of bits
    message_bit = StringToBitArray(message)

    msg_bit_idx = 0
    msg_bit_length = len(message_bit)

    # Embed message to image
    new_img = img
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            # Take each rgb pixel
            r, g, b = img[i][j]
            
            # Embed to LSB of r pixel
            new_r = (r&0xFE) + message_bit[msg_bit_idx]
            msg_bit_idx = msg_bit_idx + 1
            
            if (msg_bit_idx==msg_bit_length):
                new_pixel = [new_r, g, b]
                new_img[i][j] = new_pixel
                break
                
            # Embed to LSB of g pixel
            new_g = (g&0xFE) + message_bit[msg_bit_idx]
            msg_bit_idx = msg_bit_idx + 1    
            
            if (msg_bit_idx==msg_bit_length):
                new_pixel = [new_r, new_g, b]
                new_img[i][j] = new_pixel
                break
            
            # Embed to LSB of b pixel
            new_b = (b&0xFE) + message_bit[msg_bit_idx]
            msg_bit_idx = msg_bit_idx + 1      
            
            if (msg_bit_idx==msg_bit_length):
                new_pixel = [new_r, new_g, new_b]
                new_img[i][j] = new_pixel
                break
            
            # Set as new pixel
            new_pixel = [new_r, new_g, new_b]
            new_img[i][j] = new_pixel
        
        if (msg_bit_idx==msg_bit_length):
            break
            
    return new_img
    
def Decode(img, msg_length):
    bit_array = []
    
    # Take each LSB from each rgb pixel and save into array of bits
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r,g,b = img[i][j]
           
            # Take LSB from each rgb pixel
            bit_r = r & 0b1
            bit_g = g & 0b1
            bit_b = b & 0b1
           
            bit_array.append(str(bit_r))
            if (len(bit_array)>=(msg_length*8)):
                break
                
            bit_array.append(str(bit_g))
            if (len(bit_array)>=(msg_length*8)):
                break
                
            bit_array.append(str(bit_b))
            if (len(bit_array)>=(msg_length*8)):
                break
        
        if (len(bit_array)>=(msg_length*8)):
                break
        
    # Split array of bits into bytes
    byte_list = [bit_array[i:i+8] for i in range(0, len(bit_array), 8)]
    
    # From each byte in list, convert into the char value
    chr_list = [chr(int("".join(msg_byte),2)) for msg_byte in byte_list]

    # Join the char into one string
    message = "".join(chr_list)
            
    return message
    
def Resize(img, new_size, method):
    return cv2.resize(img, new_size, interpolation = method)
    
def Rescale(img, scale_percent, method):
    # Rescale img using according to scale_percent and method interpolation
    new_width = int(img.shape[1] * scale_percent / 100)
    new_height = int(img.shape[0] * scale_percent / 100)
    new_size = (new_width, new_height)
    return Resize(img, new_size, method)
    
def OpenRGB(filename):
    # Open RGB image
    img = cv2.imread(filename)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img
    
def SaveRGB(img, filename):
    # Save RGB image
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, img)
    
def Score(message, original_message):
    # Calculate the score of correctness (as percentage) of the message
    # Metrics : number of same elements (and same position) as the original message
    result = [message[i]==original_message[i] for i in range(len(original_message))]
    return sum(result)/len(result)*100
    
def ErrorScore(message, original_message):
    # Calculate the mean square error / 255 between the message and original message
    result = [((ord(message[i])-ord(original_message[i]))/255)**2 for i in range(len(original_message))]
    return sum(result)
    
def StringToBitArray(message):
    # Convert string into array of bits representation (no separator per char)
    message_bit = []
    for c in message:
        for i in [7,6,5,4,3,2,1,0]:
            message_bit.append((ord(c)&(1<<i))>>i)
            
    return message_bit
    
def RescaleTest(ori_img, original_message, method):
    # Kode utama untuk mengecek ketahanan image terhadap resize dengan interpolasi method
    print("Method : " + method)
    if (method=="AREA"): 
        method = cv2.INTER_AREA
    elif (method=="LINEAR"):
        method = cv2.INTER_LINEAR
    elif (method=="CUBIC"):
        method = cv2.INTER_CUBIC
    elif (method=="NEAREST"):
        method = cv2.INTER_NEAREST
    elif (method=="LANCZOS4"):
        method = cv2.INTER_LANCZOS4
    else:
        print("Method not found")
        return
    
    for scale in range (10, 310, 10):
        stego_img = Embed(ori_img, original_message)
        
        rescaled_stego_img = Rescale(stego_img, scale, method)
        SaveRGB(rescaled_stego_img, "citra_stego_" + str(scale) + ".bmp")
    
        new_scaled_img = OpenRGB("citra_stego_" + str(scale) + ".bmp")
        new_img = Resize(new_scaled_img, (ori_width, ori_height), method)
        SaveRGB(new_img, "citra_stego_new_" + str(scale) + ".bmp")
        
        message = Decode(new_img, len(original_message))
        message_bit = StringToBitArray(message)
        print(scale, Score(message_bit, original_message_bit), Score(message,original_message), ErrorScore(message,original_message), sep=',')
        
    print()

if (__name__ == "__main__"):
    # Get message from file
    message_file = open("message.txt","r")
    original_message = message_file.read()
    original_message_bit = StringToBitArray(original_message)
    
    # Open cover image
    ori_img = OpenRGB("citra_ori.bmp")
    ori_width = ori_img.shape[1]
    ori_height = ori_img.shape[0]
    
    # Test
    RescaleTest(ori_img, original_message, method = "AREA")
    RescaleTest(ori_img, original_message, method = "LINEAR")
    RescaleTest(ori_img, original_message, method = "CUBIC")
    RescaleTest(ori_img, original_message, method = "NEAREST")
    RescaleTest(ori_img, original_message, method = "LANCZOS4")