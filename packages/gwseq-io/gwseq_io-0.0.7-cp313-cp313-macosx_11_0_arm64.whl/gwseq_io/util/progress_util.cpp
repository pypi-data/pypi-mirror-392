#include "includes.cpp"


class ProgressTracker {
    i64 total;
    i64 current = 0;
    std::function<void(i64, i64)> callback;
    f64 report_interval;
    f64 last_reported = 0.0;
    std::mutex update_mutex;

public:
    ProgressTracker(
        i64 total,
        std::function<void(i64, i64)> callback,
        f64 report_interval = 0.01
    ) : total(total), callback(callback), report_interval(report_interval) {}

    void add(i64 value) {
        std::lock_guard<std::mutex> lock(update_mutex);
        current += value;
        f64 progress = (total > 0) ? static_cast<f64>(current) / total : 0.0;
        if (callback && progress > last_reported + report_interval) {
            last_reported = progress;
            callback(current, total);
        }
    }

    void done() {
        std::lock_guard<std::mutex> lock(update_mutex);
        if (callback && last_reported < 1.0) {
            last_reported = 1.0;
            callback(total, total);
        }
    }

};


class ProgressCallback {
    std::chrono::steady_clock::time_point start_time;
    bool started = false;
    
public:
    void operator()(i64 current, i64 total) {
        if (!started) {
            start_time = std::chrono::steady_clock::now();
            started = true;
        }
        i64 progress =  static_cast<i64>(static_cast<f64>(current) / total * 100);
        auto now = std::chrono::steady_clock::now();
        f64 elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count() / 1000.0;
        char progress_str[5];
        snprintf(progress_str, sizeof(progress_str), "%3lld%%", progress);
        std::cerr << "Progress: " << progress_str;
        if (current > 0 && progress < 100 && elapsed > 0) {
            f64 rate = static_cast<f64>(current) / elapsed;
            f64 remaining_items = total - current;
            std::cerr << " (ETA " << format_time(remaining_items / rate) << ")";
        } else if (progress == 100) {
            std::cerr << " (" << format_time(elapsed, 3) << ")";
        } else {
            std::cerr << "               ";
        }
        std::cerr << "  " << (current == total ? "\n" : "\r") << std::flush;
    }
};
