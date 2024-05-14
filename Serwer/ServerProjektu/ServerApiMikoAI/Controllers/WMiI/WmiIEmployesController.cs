using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Org.BouncyCastle.Crypto.Modes.Gcm;
using ServerApiMikoAI.Models.Context;
using Microsoft.EntityFrameworkCore;
using System.Configuration;
using System.Data;
using Swashbuckle.AspNetCore.Annotations;
using Microsoft.AspNetCore.Authorization;
using ServerApiMikoAI;

namespace ServerApiMikoAI.Controllers.WMiI {
    [Route("[controller]")]
    [ApiController]
    public class WmiIEmployesController : ControllerBase {
        private readonly WMiIEmployeesDatabase _context;
        private readonly AuthorizationService _authorizationService;

        public WmiIEmployesController(WMiIEmployeesDatabase context, AuthorizationService authorization) {
            _context = context;
            _authorizationService = authorization;
        }

        [HttpGet]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "get")]
        public async Task<IActionResult> GetEmployeesStatus() {

            string deviceId = HttpContext.Request.Headers["device_id"];
            string apiKey = HttpContext.Request.Headers["api_key"];
            
            var isAuthorized = await _authorizationService.IsDeviceAuthorized(deviceId, apiKey);

            if (!isAuthorized) {
                return Unauthorized("Invalid DeviceId or ApiKey.");
            }

            try {
                var lampki = _context.lampki.Select(lampka => new {
                    Name = (lampka.pole1 ?? "") + " " + (lampka.pole2 ?? "") + " " + (lampka.pole3 ?? ""),
                    Office = lampka.pole4 ?? "",
                    IsWorking = lampka.stan
                }).ToList();

                return Ok(lampki);
            }
            catch (Exception ex) {
                return StatusCode(500, $"Internal server error: {ex.Message}");
            }
        }
    }
}
