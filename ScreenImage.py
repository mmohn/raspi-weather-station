from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

class ScreenImage:

    def __init__(self, width, height):

        self.width = width;
        self.height = height;
        
        self.font_huge = ImageFont.truetype("LiberationSans-Bold.ttf", 24);
        self.font_tall = ImageFont.truetype("LiberationSansNarrow-Regular.ttf", 24);
        self.font_medium = ImageFont.truetype("LiberationSans-Regular.ttf", 16);
        self.font_thin = ImageFont.truetype("LiberationSansNarrow-Regular.ttf", 16);
        self.font_small = ImageFont.truetype("LiberationSans-Regular.ttf", 12);
        self.font_tiny = ImageFont.truetype("LiberationSans-Regular.ttf", 8);

        image = Image.open("./resources/bitmaps/temperature.png");
        self.bg_temperature = image.convert("1");

        image = Image.open("./resources/bitmaps/pressure.png");
        self.bg_pressure = image.convert("1");

        image = Image.open("./resources/bitmaps/humidity.png");
        self.bg_humidity = image.convert("1");

        image = Image.open("./resources/bitmaps/off.png");
        self.bg_shutdown = image.convert("1");

        self.set_empty();


    def set_empty(self):
        self.image = Image.new("1", (self.width, self.height));
        self.draw = ImageDraw.Draw(self.image);


    def set_background(self, background):
        self.image = background.copy();
        self.draw = ImageDraw.Draw(self.image);


    def draw_values(self, labels, values, units, digits=1):

        # background image
        if labels[1] == 'temperature':
            self.set_background(self.bg_temperature);
        elif labels[1] == 'pressure':
            self.set_background(self.bg_pressure);
        elif labels[1] == 'humidity':
            self.set_background(self.bg_humidity);
        else:
            self.set_empty();

        # centered value
        text = f"{values[1]:.1f}";
        w1, h1 = self.draw.textsize(text, font=self.font_huge);
        y = (height-h1)/2;
        x = (width-w1)/2;
        self.draw.text((x,y), text, font=self.font_huge, fill=255);
        text = units[1];
        if text.startswith(' '):
            text = text[1:];
        w2, h2 = self.draw.textsize(text, font=self.font_small);
        y = (height-h1)/2+(h1-h2);
        x = width-2-w2;
        self.draw.text((x,y), text, font=self.font_small, fill=255);

        # top value
        text = f"{values[0]:.1f}{units[0]:s}";
        wt, ht = self.draw.textsize(text, font=self.font_thin);
        y = 2;
        x = (width-wt)/2;
        self.draw.text((x,y), text, font=self.font_thin, fill=255);

        # bottom value
        text = f"{values[2]:.1f}{units[2]:s}";
        wb, hb = self.draw.textsize(text, font=self.font_thin);
        y = height-2-hb;
        x = (width-wb)/2;
        self.draw.text((x,y), text, font=self.font_thin, fill=255);


    def draw_datetime(self, show_seconds=False):
        
        self.set_empty();
        
        # centered value (time)
        now = datetime.now();
        if show_seconds:
            text = now.strftime("%H:%M:%S");
        else:
            text = now.strftime("%H:%M");
        w1, h1 = self.draw.textsize(text, font=self.font_huge);
        y = (height-h1)/2;
        x = (width-w1)/2;
        self.draw.text((x,y), text, font=self.font_huge, fill=255);

        # top value (date)
        text = now.strftime("%Y-%m-%d");
        wt, ht = self.draw.textsize(text, font=self.font_small);
        y = 2;
        x = (width-wt)/2;
        self.draw.text((x,y), text, font=self.font_small, fill=255);

        # bottom value (day of week)
        text = now.strftime("%A");
        wb, hb = self.draw.textsize(text, font=self.font_small);
        y = height-2-hb;
        x = (width-wb)/2;
        self.draw.text((x,y), text, font=self.font_small, fill=255);

    
    def draw_shutdown(self):
    
        # set image
        self.set_background(self.bg_shutdown);


    def draw_heading(self, heading):
        
        self.set_empty();

        w1, h1 = self.draw.textsize(heading, font=self.font_huge);
        y = (height-h1)/2;
        x = (width-w1)/2;
        self.draw.text((x,y), heading, font=self.font_huge, fill=255);


    def draw_message(self, message):

        self.set_empty();

        w1, h1 = self.draw.textsize(message, font=self.font_medium);
        y = (height-h1)/2;
        x = (width-w1)/2;
        self.draw.text((x,y), message, font=self.font_medium, fill=255);


    def draw_selection(self, message, selection):

        self.set_empty();

        w1, h1 = self.draw.textsize(message, font=self.font_medium);
        y = (height-h1)/2 - h1;
        y = 0 if y < 0 else y;
        x = (width-w1)/2;
        self.draw.text((x,y), message, font=self.font_medium, fill=255);
        
        w2, h2 = self.draw.textsize(selection, font=self.font_small);
        y = (height-h2)/2 + h2;
        x = (width-w2)/2;
        self.draw.text((x,y), selection, font=self.font_small, fill=255);


if __name__ == "__main__":

    import board
    import busio
    from digitalio import DigitalInOut, Direction, Pull
    import adafruit_ssd1306;
    from time import sleep;

    # create the I2C interface
    i2c = busio.I2C(board.SCL, board.SDA);
    # create the SSD1306 OLED class
    disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c);
    width = disp.width;
    height = disp.height;
    print(f"{width:d} x {height:d} image");
    disp.fill(0);
    disp.show();

    labels = ["humidity", "temperature", "pressure"];
    values = [67, 23.0342, 1003.53];
    units = ["%", "°C", " hPa"];

    for i in range(3):
        labels.insert(0, labels.pop());
        values.insert(0, values.pop());
        units.insert(0, units.pop());
        screen_image = ScreenImage(width, height);
        screen_image.draw_values(labels, values, units);
        disp.image(screen_image.image);
        disp.show();
        sleep(2);

    for show_seconds in [True, False]:
        screen_image.draw_datetime(show_seconds=show_seconds);
        disp.image(screen_image.image);
        disp.show();
        sleep(2);

    heading = "Heading";
    screen_image = ScreenImage(width, height);
    screen_image.draw_heading(heading);
    disp.image(screen_image.image);
    disp.show();
    sleep(2);

    message = "Switch off?";
    screen_image = ScreenImage(width, height);
    screen_image.draw_message(message);
    disp.image(screen_image.image);
    disp.show();
    sleep(2);

    screen_image.draw_shutdown();
    disp.image(screen_image.image);
    disp.show();
    sleep(2);

    message = "Show seconds";
    selection = "Enabled";
    screen_image = ScreenImage(width, height);
    screen_image.draw_selection(message, selection);
    disp.image(screen_image.image);
    disp.show();
    sleep(2);
