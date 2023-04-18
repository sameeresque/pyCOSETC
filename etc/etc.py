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
import chromepaths

binary_location = chromepaths.binary_location
driver_location = chromepaths.driver_location

cenwav_map = {'g130m':1310,'g160m':1602,'g140l':1282,'g185m':1835,'g225m':2135,'g285m':2850,'g230l':3000}
choose_cenwav = {'g130m':[1055,1096,1222,1291,1300,1309,1318,1327],'g160m':[1533,1577,1589,1600,1611,1623]}

g130m_band = {'1055':[924,1040,1056,1195],'1096':[941,1080,1097,1236],
             '1222':[1069,1207,1223,1363],'1291':[1137,1274,1292,1432],
             '1300':[1147,1283,1302,1441],'1309':[1154,1293,1310,1448],
             '1318':[1164,1303,1319,1459],'1327':[1173,1312,1328,1468]}

g160m_band = {'1533':[1342,1515,1533,1707],'1577':[1387,1557,1578,1749],
             '1589':[1398,1567,1590,1761],'1600':[1411,1580,1602,1772],
             '1611':[1421,1592,1612,1784],'1623':[1434,1604,1625,1796]}

def getdust(ra_deg,dec_deg):
    """
    Function to fetch the extinction value

    Parameters
    ----------
    ra_deg : float
        RA of the source of interest in degrees.

    dec_deg: float
        DEC of the source of interest in degrees.

    Returns
    -------
    tuple
        Extinction value E(B-V).
    """
    
    table = IrsaDust.get_query_table("{} {}".format(ra_deg,dec_deg), radius=2 * u.deg,section='ebv')
    return table['ext SandF mean'].quantity[0]


def cosetc(detector,grating,aperturetype,snrval,redshift_qso,qso_ra,qso_dec,redshift_abs,fuvval,wav_int):
    """
    Exposure time calculator for COS G130M/G160M gratings 
    
    Parameters
    ----------
    detector : str
        "fuv" (currently only setup for FUV)
    
    grating : str
        Valid values: "g130m", "g160m" 
    
    snrval : float
        exposure time is calculated for this desired SNR.

    apeturetype: str
        Valid values: "PSA", "BOA"
        PSA stands for Primary Sciene Aperture. BOA stands for Bright Object Aperture.
        
    redshift_qso: float
        Redshift of the QSO or the object of interest.
    
    qso_ra: float
        RA in degrees needed for determining the extinction.

    qso_dec: float
        DEC in degrees

    redshift_abs: float
        Redshift of the foreground object which is used to determine the observed wavelength at which required SNR is to be reached.
        
    fuvval: float
        FUV magnitudes from GALEX or from UV spectra if available. 
    
    wav_int: integer
        Rest wavelength of the transition of interest at which the required SNR is to be reached.
    

    Returns
    -------
    float
        Exposure time in seconds.
    """

    
    try:
        options=Options()
        options.headless = False

        options.binary_location = binary_location

        driver = webdriver.Chrome(driver_location,chrome_options=options)

        driver.get("https://etc.stsci.edu/etc/input/cos/spectroscopic/")
        
        # Selecting the detector+grating combination based on the value of these inputs
        driver.find_element("xpath",".//input[@type='radio' and @value='{}_0{}']".format(detector,grating)).click()
        # Selecting the central wavelength
        select=Select(driver.find_element("name",'{}_CentralWavelength'.format(grating.upper())))

        obs_wav = wav_int*(1.0+redshift_abs)
        choose_wav =  min(choose_cenwav[grating], key=lambda x:abs(x-obs_wav))

        select.select_by_value('{}'.format(choose_wav))

        # Selecting the Aperture
        select=Select(driver.find_element("name",'cosaperture0'))
        select.select_by_value('{}'.format(aperturetype))
        

        # Inputting the S/N ratio
        driver.find_element("xpath",".//input[@type='radio' and @value='Time']").click()

        snr=driver.find_element("name",'SNR')
        snr.clear()
        val = snrval
        snr.send_keys('{}'.format(val))

        # determining the observed wavelength at which the expected S/N is desired. The following conditions ensure that the observed wavelength is within the disperser passbands.
        
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

        # selecting the point source option
        driver.find_element("xpath",".//input[@type='radio' and @value='point']").click()


        # selecting the SED of Non-Stellar Objects
        driver.find_element("xpath",".//input[@type='radio' and @value='SpectrumNonStellar']").click()

        select=Select(driver.find_element("name",'fnonstellar'))

        # Selecting the QSO COS based spectrum
        select.select_by_value('QSO COS ')

        # selecting the extinction relationship. Using an average Galactic extinction curve for diffuse ISM (Rv=3.1).
        select=Select(driver.find_element("name",'febmvtype'))
        select.select_by_value('mwavg')

        # Inputting the extinction value and applying it before normalization.
        febv=driver.find_element("name",'febv')
        febv.clear()
        val = getdust(qso_ra,qso_dec).value
        febv.send_keys('{}'.format(val))

        select=Select(driver.find_element("name",'fextinctiontype'))
        select.select_by_value('before')


        # The SED is redshifted based on this value.
        z=driver.find_element("name",'fRedshift')
        z.clear()
        val = redshift_qso
        z.send_keys('{}'.format(val))

        driver.find_element("xpath",".//input[@type='radio' and @value='fnormalize.bandpass']").click()

        # normalizing the target flux. AB magnitudes and Galex/FUV.
        fuvmag=driver.find_element("name",'rn_flux_bandpass')
        fuvmag.clear()
        val = fuvval
        fuvmag.send_keys('{}'.format(val))

        select=Select(driver.find_element("name",'rn_flux_bandpass_units'))
        select.select_by_value('abmag')

        driver.find_element("xpath",".//input[@type='radio' and @value='fNormalizeByFilter.sloan']").click()
        select=Select(driver.find_element("name",'filter.sloan'))
        select.select_by_value('Galex/FUV')


        # Background levels for Zodiacal Light, Earth Shine, and Air Glow, all are set to Averages.
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
        
        #returns the time in seconds and number of orbits.
        try:
            return float(time.split(',')[0]+time.split(',')[1])
        except:
            return float(time)
        
    except (UnexpectedAlertPresentException,AttributeError) as e:
        print (e)
        return np.nan
        

