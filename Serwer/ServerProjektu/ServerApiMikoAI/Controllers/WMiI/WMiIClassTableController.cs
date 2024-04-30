using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System.Net;
using System.Net.Http;

namespace ServerApiMikoAI.Controllers.WMiI
{
    [Route("api/[controller]")]
    [ApiController]
    public class WMiIClassTableController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public WMiIClassTableController()
        {
            _httpClient = new HttpClient();
        }
        [HttpGet]
        public async Task<ActionResult<IEnumerable<string>>> Get()
        {
            try
            {
                // Konfiguracja przeglądarki Selenium
                var options = new ChromeOptions();
                options.AddArgument("--headless"); // Tryb headless, bez interfejsu graficznego
                options.AddArgument("--disable-gpu");
                options.AddArgument("--no-sandbox");
                options.AddArgument("--disable-dev-shm-usage");

                // Inicjalizacja przeglądarki
                using (var driver = new ChromeDriver(options))
                {
                    // Logowanie do strony
                    await Login(driver);
                    //var reservationWebsite = "https://www.mat.umk.pl/group/wmii/rezerwacje-sal?p_p_id=Rezerwacje_WAR_Rezerwacje10_INSTANCE_HFe5UNNXD2cc&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&op=ff&date=";
                    //DateTime currentDate = DateTime.Now;
                    //var reservationDate = currentDate.ToString("yyyy-MM-dd");
                    //var reservationDateString = reservationWebsite + reservationDate;
                    var reservationDateString = "https://www.mat.umk.pl/group/wmii/rezerwacje-sal?p_p_id=Rezerwacje_WAR_Rezerwacje10_INSTANCE_HFe5UNNXD2cc&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=1&op=ff";
                    // Przejście do strony z danymi do scrapowania
                    driver.Navigate().GoToUrl(reservationDateString);

                    // Pobranie danych ze strony
                    var tableElement = driver.FindElement(By.XPath(".//table"));
                    var tableRows = tableElement.FindElements(By.XPath(".//tr"));
                    var reservationInfo = new List<string>();

                    foreach (var row in tableRows)
                    {
                        var cells = row.FindElements(By.XPath(".//td"));
                        foreach (var cell in cells)
                        {
                            reservationInfo.Add(cell.Text);
                        }
                    }

                    return Ok(reservationInfo);
                }
            }
            catch (Exception ex)
            {
                return StatusCode((int)HttpStatusCode.InternalServerError, ex.Message);
            }
        }
        private async Task Login(IWebDriver driver)
        {
            // Dane do logowania
            var username = "user";
            var password = "password";

            // Przejście do strony logowania
            driver.Navigate().GoToUrl("https://www.mat.umk.pl/web/wmii/glowna?p_p_id=58&p_p_lifecycle=0&p_p_state=maximized&p_p_mode=view&saveLastPath=false&_58_struts_action=%2Flogin%2Flogin");

            // Wypełnienie formularza logowania
            var usernameInput = driver.FindElement(By.XPath("//form//input[contains(@id,'login')]"));
            //var usernameInput = driver.FindElement(By.CssSelector("//div[@class=' portlet-content-container']/div[@class='portlet-body']/center/div[@class='ti-container']/div[@class='ti-employee'][1]/div[@class='ti-name']"));
            usernameInput.SendKeys(username);

            var passwordInput = driver.FindElement(By.XPath("//form//input[contains(@id,'password')]"));
            passwordInput.SendKeys(password);

            // Zatwierdzenie formularza
            var loginButton = driver.FindElement(By.CssSelector(".btn-primary"));
            loginButton.Click();

            // Poczekaj na zalogowanie się (możesz dodać bardziej zaawansowane metody oczekiwania)
            await Task.Delay(5000);
        }
    }
}
