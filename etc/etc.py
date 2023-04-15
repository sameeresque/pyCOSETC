import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.cosmology import FlatLambdaCDM
from astroquery.irsa_dust import IrsaDust
import astropy.units as u
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
import math

def getdust(ra_deg,dec_deg):
    table = IrsaDust.get_query_table("{} {}".format(ra_deg,dec_deg), radius=2 * u.deg,section='ebv')
    return table['ext SandF mean'].quantity[0]


def cosetc(detector,grating,snrval,redshift_qso,qso_ra,qso_dec,redshift_abs,fuvval,wav_int):
    """
    Exposure time calculator for COS G130M/G160M gratings 
    
    Parameters
    ----------
    detector : str
    "fuv"
    
    grating : str
    
    "g130m" or "g160m" 
    
    snrval : float
    
    exposure time is calculated for this SNR
    
    extinction: float
    
    value of extinction in the direction of source
    
    redshift_qso: float
    
    Redshift of the background source
    
    redshift_abs: float
    
    Redshift of the foreground object
    
    fuvval: float
    
    FUV Magnitude
    
    wav_int: integer
    
    wavelength of interest
    

    Returns
    -------
    Exposure time in seconds
    """

    
    try:
        options=Options()
        options.headless = False

        options.binary_location = "/usr/bin/google-chrome"

        driver = webdriver.Chrome('/home/sameer/Downloads/chromedriver_linux64/chromedriver',chrome_options=options)

        driver.get("https://etc.stsci.edu/etc/input/cos/spectroscopic/")
        
        
        driver.find_element("xpath",".//input[@type='radio' and @value='{}_0{}']".format(detector,grating)).click()
        select=Select(driver.find_element("name",'{}_CentralWavelength'.format(grating.upper())))

        obs_wav = wav_int*(1.0+redshift_abs)
        choose_wav =  min(choose_cenwav[grating], key=lambda x:abs(x-obs_wav))

        select.select_by_value('{}'.format(choose_wav))

        driver.find_element("xpath",".//input[@type='radio' and @value='Time']").click()

        snr=driver.find_element("name",'SNR')
        snr.clear()
        val = snrval
        snr.send_keys('{}'.format(val))

        central=driver.find_element("name",'obswave')
        central.clear()



        if grating == 'g130m':
            arrayin = np.asarray(g130m_band[str(choose_wav)])

            ind = (np.abs(arrayin - obs_wav)).argmin()

            if (obs_wav < g130m_band[str(choose_wav)][2]) and (obs_wav > g130m_band[str(choose_wav)][1]):
                if ind == 2:
                    val = (g130m_band[str(choose_wav)][2]+g130m_band[str(choose_wav)][3])*0.5
                else:
                    val = (g130m_band[str(choose_wav)][0]+g130m_band[str(choose_wav)][1])*0.5
            else:
                val = obs_wav


        elif grating == 'g160m':
            arrayin = np.asarray(g160m_band[str(choose_wav)])

            ind = (np.abs(arrayin - obs_wav)).argmin()

            if (obs_wav < g160m_band[str(choose_wav)][2]) and (obs_wav > g160m_band[str(choose_wav)][1]):
                if ind == 2:
                    val = (g160m_band[str(choose_wav)][2]+g160m_band[str(choose_wav)][3])*0.5
                else:
                    val = (g160m_band[str(choose_wav)][0]+g160m_band[str(choose_wav)][1])*0.5
            else:
                val = obs_wav


        else:
            print ("Grating not yet setup!")

        central.send_keys('{}'.format(val))


        driver.find_element("xpath",".//input[@type='radio' and @value='point']").click()
        driver.find_element("xpath",".//input[@type='radio' and @value='SpectrumNonStellar']").click()

        select=Select(driver.find_element("name",'fnonstellar'))
        select.select_by_value('QSO COS ')

        select=Select(driver.find_element("name",'febmvtype'))
        select.select_by_value('mwavg')

        febv=driver.find_element("name",'febv')
        febv.clear()
        val = getdust(qso_ra,qso_dec).value
        febv.send_keys('{}'.format(val))

        select=Select(driver.find_element("name",'fextinctiontype'))
        select.select_by_value('before')

        z=driver.find_element("name",'fRedshift')
        z.clear()
        val = redshift_qso
        z.send_keys('{}'.format(val))

        driver.find_element("xpath",".//input[@type='radio' and @value='fnormalize.bandpass']").click()


        fuvmag=driver.find_element("name",'rn_flux_bandpass')
        fuvmag.clear()
        val = fuvval
        fuvmag.send_keys('{}'.format(val))

        select=Select(driver.find_element("name",'rn_flux_bandpass_units'))
        select.select_by_value('abmag')

        driver.find_element("xpath",".//input[@type='radio' and @value='fNormalizeByFilter.sloan']").click()
        select=Select(driver.find_element("name",'filter.sloan'))
        select.select_by_value('Galex/FUV')

        driver.find_element("xpath",".//input[@type='radio' and @value='ZodiStandard']").click()
        select=Select(driver.find_element("name",'ZodiStandard'))
        select.select_by_value('Average')


        driver.find_element("xpath",".//input[@type='radio' and @value='EarthshineStandard']").click()
        select=Select(driver.find_element("name",'EarthshineStandard'))
        select.select_by_value('Average')

        select=Select(driver.find_element("name",'AirglowStandard'))
        select.select_by_value('Average')

        driver.find_element("xpath",".//input[@type='button' and @value='Submit Simulation']").click()

        soup = BeautifulSoup(driver.page_source)
        ps=soup.find_all('p')

        
        time = ps[2].string.split(' ')[3]
        
        
        try:
            return float(time.split(',')[0]+time.split(',')[1]),math.ceil(float(time.split(',')[0]+time.split(',')[1])/60./49.)
        except:
            return float(time),math.ceil(float(time)/60./49.)
        
    except (UnexpectedAlertPresentException,AttributeError) as e:
        print (e)
        return np.nan
        

