package __BASE_PACKAGE__.repository;

import __BASE_PACKAGE__.domain.Reservation;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * 예약 Repository
 * - DB CRUD 담당
 */
public interface ReservationRepository extends JpaRepository<Reservation, Long> {
    
}