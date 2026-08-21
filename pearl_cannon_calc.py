import struct
import argparse
import sys

# ========== 函数定义在最前面 ==========
def float32_to_float64(val):
    packed = struct.pack('!f', val)
    unpacked = struct.unpack('!f', packed)[0]
    return float(unpacked)

def num_to_bits(num):
    values = [80, 40, 20, 10, 4, 3, 2, 1]
    bits = []
    for v in values:
        if num >= v:
            bits.append('1')
            num -= v
        else:
            bits.append('0')
    bit_str = ''.join(bits)
    return f"{bit_str[:4]} {bit_str[4:]}"

# ========== 物理常量（现在函数已定义，可以安全调用）==========
G = 0.03
F = float32_to_float64(0.99)
ONE_TNT_MOTION_XZ = 0.6026793588895138
ONE_TNT_MOTION_Y = 0.004435058914919521
DIRECTIONS_MAPPING = {'N': '00', 'W': '01', 'E': '10', 'S': '11'}

def main():
    parser = argparse.ArgumentParser(description='珍珠炮炮码计算器')
    parser.add_argument('--dest-x', type=float, required=True, help='目标 X 坐标')
    parser.add_argument('--dest-z', type=float, required=True, help='目标 Z 坐标')
    parser.add_argument('--base-tick', type=int, required=True, help='基准时刻 tick 数')
    parser.add_argument('--base-pos', type=float, nargs=3, required=True, help='基准位置 x y z')
    parser.add_argument('--base-motion', type=float, nargs=3, required=True, help='基准速度 vx vy vz')
    parser.add_argument('--ground-height', type=float, default=128, help='地面高度（默认128）')

    args = parser.parse_args()

    dest_x = args.dest_x
    dest_z = args.dest_z
    base_tick = args.base_tick
    ground_height = args.ground_height
    pos0 = args.base_pos
    motion0 = args.base_motion

    dx = dest_x - pos0[0]
    dz = dest_z - pos0[2]

    if abs(dx) > abs(dz):
        direction = 'E' if dx > 0 else 'W'
    else:
        direction = 'S' if dz > 0 else 'N'

    last_error = float('inf')
    fly_tick = 1

    while True:
        kp = 2 * ONE_TNT_MOTION_XZ * ((F - F ** (fly_tick + 1)) / (1 - F))

        if direction in ('N', 'S'):
            m = round((dx + dz) / kp)
            n = round((dz - dx) / kp)
            if direction == 'N':
                m, n = n, m
            motion_x = (abs(m) - abs(n)) * ONE_TNT_MOTION_XZ + motion0[0]
            motion_y = abs(m + n) * ONE_TNT_MOTION_Y + motion0[1]
            motion_z = (m + n) * ONE_TNT_MOTION_XZ + motion0[2]
        else:
            m = round((dx + dz) / kp)
            n = round((dx - dz) / kp)
            if direction == 'W':
                m, n = n, m
            motion_x = (m + n) * ONE_TNT_MOTION_XZ + motion0[0]
            motion_y = abs(m + n) * ONE_TNT_MOTION_Y + motion0[1]
            motion_z = (abs(m) - abs(n)) * ONE_TNT_MOTION_XZ + motion0[2]

        if abs(m) > 160 or abs(n) > 160:
            fly_tick += 1
            continue

        px, py, pz = pos0
        vx, vy, vz = motion_x, motion_y, motion_z
        for _ in range(fly_tick):
            vx *= F
            vy = (vy - G) * F
            vz *= F
            px += vx
            py += vy
            pz += vz

        if py <= ground_height:
            break

        error = (px - dest_x) ** 2 + (pz - dest_z) ** 2
        if error < last_error:
            code = (num_to_bits(round(abs(n)))[::-1] + " " +
                    DIRECTIONS_MAPPING[direction] + " " +
                    num_to_bits(round(abs(m))))
            total_tick = fly_tick + base_tick
            print(f"tick cost:{fly_tick} code:{code}  tick: {total_tick}   Pos: [{px:.2f}, {py:.2f}, {pz:.2f}]  error:{error**0.5:.2f}")
            last_error = error

        fly_tick += 1

if __name__ == '__main__':
    main()