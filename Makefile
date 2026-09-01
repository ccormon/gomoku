NAME := Gomoku
CXX := c++
CXXFLAGS := -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Werror -fPIC -Iinclude
LDFLAGS := -shared

BUILD_DIR := build
CPP_SOURCES := src/cpp/engine.cpp src/cpp/c_api.cpp
OBJECTS := $(CPP_SOURCES:src/cpp/%.cpp=$(BUILD_DIR)/%.o)
LIBRARY := $(BUILD_DIR)/libgomoku_ai.so

.PHONY: all clean fclean re test bench

all: $(NAME)

$(NAME): scripts/Gomoku $(LIBRARY)
	cp scripts/Gomoku $(NAME)
	chmod +x $(NAME)

$(LIBRARY): $(OBJECTS)
	$(CXX) $(LDFLAGS) $^ -o $@

$(BUILD_DIR)/%.o: src/cpp/%.cpp include/gomoku/engine.hpp include/gomoku/c_api.h
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/test_engine: tests/cpp/test_engine.cpp src/cpp/engine.cpp include/gomoku/engine.hpp
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) tests/cpp/test_engine.cpp src/cpp/engine.cpp -o $@

test: all $(BUILD_DIR)/test_engine
	$(BUILD_DIR)/test_engine
	python3 -m unittest discover -s tests/python -v

bench: all
	python3 -m unittest tests.python.test_performance -v

clean:
	rm -f $(OBJECTS) $(BUILD_DIR)/test_engine

fclean: clean
	rm -f $(LIBRARY) $(NAME)

re: fclean all
