package __BASE_PACKAGE__.domain;

import jakarta.persistence.*;

/**
 * 예약 엔티티
 * - DB 테이블과 매핑되는 클래스
 */
@Entity
public class Reservation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name; // 예약자 이름

    private String date; // 예약 날짜

    protected Reservation() {
        
    }

    public Reservation(String name, String date) {
        this.name = name;
        this.date = date;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getDate() {
        return date;
    }
}