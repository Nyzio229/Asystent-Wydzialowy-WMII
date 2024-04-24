using Microsoft.EntityFrameworkCore;


namespace ServerApiMikoAI.Models.Context
{
    public class PostrgeSQLContext : DbContext
    {
        public PostrgeSQLContext(DbContextOptions<PostrgeSQLContext> options) : base(options)
        { }

        public DbSet<TableContext> asystentwydzialowy_faq { get; set; }
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<TableContext>().HasKey(t => t.id_pytania);
        }
    }
}
