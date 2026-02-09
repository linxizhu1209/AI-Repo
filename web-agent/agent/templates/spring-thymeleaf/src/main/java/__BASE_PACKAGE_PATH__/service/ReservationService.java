package __BASE_PACKAGE__.service;

import __BASE_PACKAGE__.domain.Reservation;
import __BASE_PACKAGE__.repository.ReservationRepository;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * 예약 서비스
 * - 비즈니스 로직 담당
 */
@Service
public class ReservationService {
    private final ReservationRepository repository;

    public ReservationService(ReservationRepository repository) {
        this.repository = repository;
    }

    /**
     * 예약 목록 조회
     */
    public List<Reservation> findAll() {
        return repository.findAll();
    }

    /**
     * 예약 생성
     */
    public Reservation create(String name, String date) {
        return repository.save(new Reservation(name, date));
    }
}