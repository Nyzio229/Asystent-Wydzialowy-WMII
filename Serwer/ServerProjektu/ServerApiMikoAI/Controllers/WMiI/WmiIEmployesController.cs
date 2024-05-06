using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Org.BouncyCastle.Crypto.Modes.Gcm;
using ServerApiMikoAI.Models.Context;
using Microsoft.EntityFrameworkCore;
using System.Configuration;
using System.Data;
using Swashbuckle.AspNetCore.Annotations;

namespace ServerApiMikoAI.Controllers.WMiI {
    [Route("[controller]")]
    [ApiController]
    public class WmiIEmployesController : ControllerBase {
        private readonly WMiIDataBase _context;
        public WmiIEmployesController(WMiIDataBase context) {
            _context = context;
        }
        [HttpGet]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "get")]
        public async Task<IActionResult> GetEmployeesStatus() {

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
