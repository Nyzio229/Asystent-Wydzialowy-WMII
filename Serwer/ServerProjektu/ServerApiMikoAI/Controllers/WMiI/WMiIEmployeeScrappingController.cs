using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Net;
using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;

namespace ServerApiMikoAI.Controllers.WMiI
{
    [Route("api/[controller]")]
    [ApiController]
    public class WMiIEmployeeScrappingController : ControllerBase
    {
        private readonly HttpClient _httpClient;

        public WMiIEmployeeScrappingController()
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

                    // Przejście do strony z danymi do scrapowania
                    driver.Navigate().GoToUrl("https://www.mat.umk.pl/group/wmii/tablica-informacyjna");

                    // Pobranie danych ze strony
                    //var scrapedData = driver.FindElement(By.XPath("//div[@class='ti-container']")).Text;
                    //var images = driver.FindElements(By.XPath($"/images/{scrapedData}"));

                    //return Ok(scrapedData);

                    var employeeElements = driver.FindElements(By.ClassName("ti-employee"));
                    var employeeInfo = new List<string>();

                    foreach (var employee in employeeElements)
                    {
                        var lampElement = employee.FindElement(By.ClassName("ti-lamp"));
                        var lampImage = lampElement.FindElement(By.TagName("img"));
                        var src = lampImage.GetAttribute("src");
                        var alt = lampImage.GetAttribute("alt");

                        var nameElement = employee.FindElement(By.ClassName("ti-name"));
                        var name = nameElement.Text;

                        var roomElement = employee.FindElement(By.ClassName("ti-room"));
                        var room = roomElement.Text;

                        employeeInfo.Add($"Obrazek src: {src}, alt: {alt}, Nazwa: {name}, Pokój: {room}");
                    }

                    return Ok(employeeInfo);
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
