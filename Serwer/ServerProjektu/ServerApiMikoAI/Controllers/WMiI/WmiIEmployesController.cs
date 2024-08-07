﻿using Microsoft.AspNetCore.Http;
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
    [SwaggerTag("Endpoint do sprawdzania statusu pracowników WMiI.")]
    public class WmiIEmployesController : ControllerBase {
        private readonly WMiIEmployeesDatabase _context;
        private readonly AuthorizationService _authorizationService;

        public WmiIEmployesController(WMiIEmployeesDatabase context, AuthorizationService authorization) {
            _context = context;
            _authorizationService = authorization;
        }
        /// <summary>
        /// Pobiera status pracowników WMiI.
        /// </summary>
        /// <returns>Lista statusów pracowników.</returns>
        /// <response code="200">Zwraca listę statusów pracowników.</response>
        /// <response code="401">Uwierzytelnianie nie powiodło się.</response>
        /// <response code="500">Wystąpił błąd serwera.</response>
        [HttpGet]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "get", Summary = "Pobiera status pracowników WMiI", Description = "Pobiera status pracowników Wydziału Matematyki i Informatyki Uniwersytetu Mikołaja Kopernika.")]
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
