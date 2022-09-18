from PriceStream import PriceStream

import time


pS = PriceStream('APEBUSD')

while True:
    print(pS.get_price())
    time.sleep(1)
