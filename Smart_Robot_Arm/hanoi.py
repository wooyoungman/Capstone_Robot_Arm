class HanoiTower:
    def __init__(self, n):
        # 초기 상태 설정
        self.state = {"A": list(range(1, n + 1)), "B": [], "C": []}
        # 상태 변화 기록
        self.state_history = [[self.state["A"][:], self.state["B"][:], self.state["C"][:]]]
        # 탑의 크기
        self.num_disks = n
        # 현재 탑의 상태 인덱스
        self.current_state_idx = 0
        # 하노이 탑 해결
        self.solve_hanoi(self.num_disks, "A", "C", "B")

    def solve_hanoi(self, num_disks, from_peg, to_peg, via_peg):
        # 탑 크기가 1일 경우
        if num_disks == 1:
            # 디스크 이동
            self.state[to_peg].insert(0, self.state[from_peg][0])
            self.state[from_peg].pop(0)
            # 상태 변화 기록
            self.state_history.append([self.state["A"][:], self.state["B"][:], self.state["C"][:], [from_peg, to_peg]])
        else:
            # 탑 크기가 1이 아닐 경우 재귀 호출을 통해 문제 해결
            self.solve_hanoi(num_disks - 1, from_peg, via_peg, to_peg)
            # 디스크 이동
            self.state[to_peg].insert(0, self.state[from_peg][0])
            self.state[from_peg].pop(0)
            # 상태 변화 기록
            self.state_history.append([self.state["A"][:], self.state["B"][:], self.state["C"][:], [from_peg, to_peg]])
            # 다음 재귀 호출
            self.solve_hanoi(num_disks - 1, via_peg, to_peg, from_peg)

    def get_state_history(self):
        # 상태 변화 기록 반환
        return self.state_history

    def invade_state(self, target_state):
        # 타겟 상태로 이동
        for idx, state in enumerate(self.state_history):
            if state[:3] == target_state:
                self.current_state_idx = idx
                break
