﻿using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using ServerApiMikoAI.Models.Context;
using Swashbuckle.AspNetCore.Annotations;
using Microsoft.EntityFrameworkCore;

namespace ServerApiMikoAI.Controllers.Verify {
    [Route("[controller]")]
    [ApiController]
    [SwaggerTag("Endpoint do zdezautoryzowania urządzenia.")]
    public class UnauthorizeDeviceController : ControllerBase {
        private readonly VerificationDataBaseContext _context;
        public UnauthorizeDeviceController(VerificationDataBaseContext context) {
            _context = context; 
        }
        /// <summary>
        /// Anulowanie autoryzacji urządzenia.
        /// </summary>
        /// <param name="request">Żądanie anulowania autoryzacji urządzenia.</param>
        /// <returns>Wiadomość potwierdzająca anulowanie autoryzacji urządzenia.</returns>
        /// <response code="200">Zwraca potwierdzenie anulowania autoryzacji urządzenia.</response>
        /// <response code="404">Urządzenie lub klucz API nie zostało znalezione.</response>
        [HttpPost]
        [ProducesResponseType(typeof(string), StatusCodes.Status200OK)]
        [SwaggerOperation(OperationId = "post", Summary = "Anulowanie autoryzacji urządzenia", Description = "Anulowanie autoryzacji urządzenia na podstawie przekazanego żądania.")]
        public async Task<IActionResult> UnauthorizeDevice([FromBody] LogoutRequest request) {
            // Sprawdzamy, czy istnieje wpis dla danego deviceId w tabeli api_access
            var apiAccessEntry = await _context.api_access.FirstOrDefaultAsync(a => a.device_id == request.device_id && a.api_key == request.api_key);
            var verifyTableEntry = await _context.verification_table.FirstOrDefaultAsync(a => a.device_id == request.device_id);

            if (apiAccessEntry == null) {
                return NotFound("Device not found.");
            }
            if (verifyTableEntry == null) {
                return NotFound("Device not found");
            }

            // Ustawiamy pole is_active na false dla danego urządzenia
            apiAccessEntry.is_active = false;

            // Usuwamy cały wiersz dla danego urządzenia
            _context.api_access.Remove(apiAccessEntry);
            _context.verification_table.Remove(verifyTableEntry);

            // Zapisujemy zmiany do bazy danych
            await _context.SaveChangesAsync();

            return Ok("Device logged out successfully.");
        }
    }
    public class LogoutRequest {
        public string device_id { get; set; }
        public string api_key { get; set; }
    }
}
