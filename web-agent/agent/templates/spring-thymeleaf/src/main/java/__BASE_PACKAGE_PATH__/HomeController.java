import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.ui.Model;

/**
 * 홈 화면 컨트롤러
 * - URL 요청을 받아서 어떤 화면을 보여줄지 결정
 */
@Controller
public class HomeController {

    @GetMapping("/")
    public String home(Model model) {
        // 페이지 타이틀 전달
        model.addAttribute("title", "__PROJECT_NAME__");
        return "home";
    }

}