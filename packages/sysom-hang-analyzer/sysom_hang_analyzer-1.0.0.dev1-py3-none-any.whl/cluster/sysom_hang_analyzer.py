#!/usr/bin/env python3
# deploy_distributed_stack.py

import subprocess
import sys
import os
import argparse

def deploy_coordinator(host="0.0.0.0", port=8080, dump_path="/tmp/stack_data"):
    """部署协调器（在主节点上运行）"""
    print(f"部署协调器: {host}:{port}")
    
    cmd = [
        "python3", "-m", "cluster.distributed_coordinator",
        "--host", str(host),
        "--port", str(port),
        "--dump-path", dump_path
    ]
    
    with open("/tmp/coordinator.log", "w") as log_file:
        process = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
    
    print("协调器已启动，日志: /tmp/coordinator.log")

def deploy_node_agent(coordinator_host, coordinator_port=8081, node_id=None, dump_path="/tmp/stack_data"):
    """部署节点代理（在每个训练节点上运行）"""
    if not coordinator_host:
        print("错误: 必须提供协调器主机地址")
        return 1
    
    print(f"部署节点代理，连接到: {coordinator_host}:{coordinator_port}")
    
    cmd = [
        "python3", "-m", "cluster.node_agent",
        "--coordinator-host", coordinator_host,
        "--coordinator-port", str(coordinator_port),
        "--dump-path", dump_path
    ]
    
    if node_id:
        cmd.extend(["--node-id", node_id])
    
    with open("/tmp/node_agent.log", "w") as log_file:
        process = subprocess.Popen(cmd, stdout=log_file, stderr=log_file)
    
    print("节点代理已启动，日志: /tmp/node_agent.log")

def trigger_collection(coordinator_host, coordinator_port=8080):
    """触发采集"""
    if not coordinator_host:
        print("错误: 必须提供协调器主机地址")
        return 1
    
    print("触发分布式堆栈采集...")
    
    cmd = [
        "python3", "-m", "cluster.trigger_distributed_collection",
        "--coordinator-host", coordinator_host,
        "--coordinator-port", str(coordinator_port)
    ]
    
    result = subprocess.run(cmd)
    return result.returncode

def aggregate_analysis(input_dir, output_dir):
    """聚合分析"""
    if not input_dir or not output_dir:
        print("错误: 必须提供输入和输出目录")
        return 1
    
    print("聚合分析数据...")
    
    cmd = [
        "python3", "-m", "cluster.aggregate_analysis",
        "--input-dir", input_dir,
        "--output-dir", output_dir
    ]
    
    result = subprocess.run(cmd)
    return result.returncode

def show_help():
    """显示帮助"""
    print("用法: sysom-hang-analyzer [选项]")
    print("选项:")
    print("  coordinator [host] [port] [dump_path]  - 部署协调器")
    print("  node-agent <coordinator_host> [port] [node_id] [dump_path] - 部署节点代理")
    print("  trigger <coordinator_host> [port]     - 触发采集")
    print("  aggregate <input_dir> <output_dir>     - 聚合分析")
    print("  help                                  - 显示此帮助")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1]
    
    if command == "coordinator":
        host = sys.argv[2] if len(sys.argv) > 2 else "0.0.0.0"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8080
        dump_path = sys.argv[4] if len(sys.argv) > 4 else "/tmp/stack_data"
        deploy_coordinator(host, port, dump_path)
    elif command == "node-agent":
        if len(sys.argv) < 3:
            print("错误: 必须提供协调器主机地址")
            return 1
        coordinator_host = sys.argv[2]
        coordinator_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8081
        node_id = sys.argv[4] if len(sys.argv) > 4 else None
        dump_path = sys.argv[5] if len(sys.argv) > 5 else "/tmp/stack_data"
        deploy_node_agent(coordinator_host, coordinator_port, node_id, dump_path)
    elif command == "trigger":
        if len(sys.argv) < 3:
            print("错误: 必须提供协调器主机地址")
            return 1
        coordinator_host = sys.argv[2]
        coordinator_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8080
        trigger_collection(coordinator_host, coordinator_port)
    elif command == "aggregate":
        if len(sys.argv) < 4:
            print("错误: 必须提供输入和输出目录")
            return 1
        input_dir = sys.argv[2]
        output_dir = sys.argv[3]
        aggregate_analysis(input_dir, output_dir)
    else:
        show_help()

if __name__ == "__main__":
    main()