import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.utils.data import download_file
from astropy.visualization import simple_norm

# 1. DOWNLOAD a real NASA image (The Horsehead Nebula)
image_url = 'http://data.astropy.org/tutorials/FITS-images/HorseHead.fits'
sample_file = download_file(image_url, cache=True)

# 2. OPEN the downloaded file
hdul = fits.open(sample_file)
image_data = hdul[0].data

# 3. SET UP the view (Log scale so it looks pretty)
norm = simple_norm(image_data, 'log', percent=99.5)

# 4. SHOW IT
plt.figure(figsize=(10, 8))
plt.imshow(image_data, cmap='magma', origin='lower', norm=norm)
plt.colorbar(label='Light Intensity')
plt.title('The Horsehead Nebula (FITS Data)')
plt.show()