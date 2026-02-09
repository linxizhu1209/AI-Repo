package __BASE_PACKAGE__.web;

import __BASE_PACKAGE__.service.ReservationService;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

/**
 * 예약 컨트롤러
 * - 예약 화면 요청 처리
 */
@Controller
@RequestMapping("/reservations")
public class ReservationController {
    private final ReservationService service;

    public ReservationController(ReservationService service) {
        this.service = service;
    }

    /**
     * 예약 목록 페이지
     */
    @GetMapping
    public String list(Model model) {
        model.addAttribute("reservations", service.findAll());
        return "reservation/list";
    }

    /**
     * 예약 생성 처리
     */
    @PostMapping
    public String create(
        @RequestParam String name,
        @RequestParam String date
    ) {
        service.create(name, date);
        return "redirect:/reservations";
    }
}