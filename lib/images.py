import pygame

def image_cacher():
    images = {}
    def load(image_path, convert=False, size=None):
        if (image_path, convert, size) in images:
            return images[(image_path, convert, size)]
        
        image = pygame.image.load(image_path)
        if size:
            image = pygame.transform.scale(image, size)
        if convert:
            image = image.convert()
        images[(image_path, convert, size)] = image
        
        return image
    return load

load = image_cacher()

if __name__ == '__main__':
    # make sure the image cache is working.
    pygame.init()
    pygame.display.set_mode()
    bamboo = load('../images/backgrounds/bamboo.png')
    bamboo2 = load('../images/backgrounds/bamboo.png')
    print('bamboo is bamboo2: {}'.format(bamboo is bamboo2))
    
    bg1 = load('../images/backgrounds/bamboo.png', convert=True, size=(550, 323))
    bg2 = load('../images/backgrounds/bamboo.png', convert=True, size=(550, 323))
    print('bg1 is bg2: {}'.format(bg1 is bg2))
    